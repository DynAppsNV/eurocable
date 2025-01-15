import ntpath
import os
import traceback
from datetime import datetime

from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, config

from odoo.addons.queue_job.job import identity_exact

ARCHIVE_DIR = "archive"
ERROR_DIR = "error"
GET_DIRECTION = "get"
PUT_DIRECTION = "put"
DIRECTIONS = [(GET_DIRECTION, "Get Files"), (PUT_DIRECTION, "Put Files")]
STATES = [("new", "New"), ("success", "Success"), ("error", "Error")]


class FtpFileHandler(models.Model):
    _name = "xx.ftp.file.handler"
    _description = "FTP File Handler"
    _inherit = "xx.ftp.utility"

    filename = fields.Char(
        required=True,
    )
    ftp_connection_directory_id = fields.Many2one(
        comodel_name="xx.ftp.connection.directory",
        string="FTP Connection Directory",
    )
    model_name = fields.Char(
        string="Object",
        related="ftp_connection_directory_id.model_name",
    )
    method_name = fields.Char(
        string="Method",
        related="ftp_connection_directory_id.method_name",
    )
    args = fields.Text(
        string="Arguments",
        related="ftp_connection_directory_id.args",
    )
    state = fields.Selection(
        selection=STATES,
        default="new",
    )
    process_error = fields.Text()
    process_time = fields.Datetime()
    process_message = fields.Text()
    file_on_server = fields.Boolean(compute="_compute_file_on_server")

    @api.depends("filename")
    def _compute_file_on_server(self):
        for record in self:
            record.file_on_server = os.path.exists(record.filename)

    @api.model
    def process_ftp_files(self):
        for ftp_file in self.search([("state", "=", "new")]):
            self.with_delay(
                priority=20,
                max_retries=5,
                channel=self.env.ref("dyn_ftp_transfer.channel_ftp_files_queue").name,
                description="FTP File Job",
                identity_key=identity_exact,
            )._process_ftp_file(ftp_file)

    def _process_ftp_file(self, ftp_file):
        ftp_file_env = ftp_file
        if not config["test_enable"]:
            new_env = api.Environment(self._cr, self._uid, self._context)
            ftp_file_env = ftp_file.with_env(new_env)
        try:
            ftp_file_env.process_file()
            ftp_file_env._commit()
        except Exception:
            ftp_file_env._rollback()
            ftp_file_env.get_logger().exception(
                _("Unexpected exception while processing file {filename}\n{traceback}").format(
                    filename=ftp_file.filename,
                    traceback=traceback.format_exc(),
                )
            )

    def process_file(self):
        self = self.with_user(self.ftp_connection_directory_id.user_id.id)
        filename = self.filename
        self.get_logger().info(_("Processing file '%s'") % filename)
        ctx = self.env.context.copy()
        ctx["file_handler"] = self
        if self.with_context(**ctx)._callback():
            archive_file = os.path.join(
                self.ftp_connection_directory_id.get_archive_dir(),
                ntpath.basename(filename),
            )
            self.write(
                {
                    "state": "success",
                    "process_error": False,
                    "process_time": datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    "filename": archive_file,
                }
            )
            if archive_file != filename:
                self.get_logger().info(f"Moving file {filename} to {archive_file}")
                try:
                    os.rename(filename, archive_file)
                except FileNotFoundError:
                    self.get_logger().info("No file found")
        self.get_logger().info(_("File '%s' processed") % filename)

    def view_file(self):
        return {
            "type": "ir.actions.act_url",
            "url": "/dyn_interface_file/%s" % self.id,
            "target": "new",
        }

    def _handle_callback_exception(self):
        self._rollback()
        filename = self.filename
        err_msg = _("Error occurred when processing file '%s'") % filename
        self.get_logger().exception(err_msg)
        stack = traceback.format_exc()
        err_msg += "\n\n%s" % stack
        error_file = os.path.join(
            self.ftp_connection_directory_id.get_error_dir(), ntpath.basename(filename)
        )
        self.write(
            {
                "state": "error",
                "process_error": err_msg,
                "process_time": datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                "filename": error_file,
            }
        )
        if error_file != filename:
            self.get_logger().info(f"Moving file {filename} to {error_file}")
            os.rename(filename, error_file)
