import base64
import fnmatch
import glob
import os
import stat
import time
import traceback
from datetime import datetime

import pytz

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, config

from odoo.addons.base.models.ir_cron import _intervalTypes
from odoo.addons.dyn_ftp_connection.models.ftp_connection import FTP_PROTOCOL, SFTP_PROTOCOL

ARCHIVE_DIR = "archive"
ERROR_DIR = "error"
GET_DIRECTION = "get"
PUT_DIRECTION = "put"
DIRECTIONS = [(GET_DIRECTION, "Get Files"), (PUT_DIRECTION, "Put Files")]


class FtpConnectionDirectory(models.Model):
    _inherit = "xx.ftp.utility"
    _name = "xx.ftp.connection.directory"
    _description = "FTP Connection Directory"

    ftp_connection_id = fields.Many2one(
        comodel_name="xx.ftp.connection", string="FTP Connection", required=True
    )
    name = fields.Char(string="FTP Directory", required=True)
    archive_name = fields.Char(string="Archive Directory")
    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", related="ftp_connection_id.company_id"
    )
    direction = fields.Selection(DIRECTIONS, string="FTP Direction", required=True)
    confirm_file_size = fields.Boolean(string="Confirm File Size?", default=True)
    data_dir_prefix = fields.Boolean(string="Use Data Dir as Prefix?", default=True)
    local_directory = fields.Char(required=True)
    file_mask = fields.Char(default="*", required=True)
    active = fields.Boolean(string="Active?", default=True)
    user_id = fields.Many2one(comodel_name="res.users", string="User", required=True)
    interval_number = fields.Integer(default=1, help="Repeat every x.")
    interval_type = fields.Selection(
        selection=[
            ("minutes", "Minutes"),
            ("hours", "Hours"),
            ("work_days", "Work Days"),
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
        ],
        string="Interval Unit",
        default="hours",
    )
    next_execution_date = fields.Datetime(
        required=True,
        default=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        help="Next planned execution date for this directory.",
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        help="Model name on which the method to be called is located, e.g. 'res.partner'.",
    )
    model_name = fields.Char(
        related="model_id.model", string="Model Name", readonly=True, store=True
    )
    method_name = fields.Char(
        string="Method",
        help="Name of the method to be called when this directory is processed.",
    )
    args = fields.Text(
        string="Arguments", help="Arguments to be passed to the method, e.g. (uid,)."
    )
    priority = fields.Integer(
        default=5,
        help="The priority of the directory, as an integer: 0 means higher priority,"
        "10 means lower priority.",
    )
    attach_file = fields.Boolean(string="Add imported file as attachment", default=False)
    include_subdirs = fields.Boolean(string="Include Subdirectories", default=False)
    exclude_dirs = fields.Char(
        string="Exclude Directories (comma-separated)", default="error,archive"
    )

    def process_ftp_files(self):
        self.env["xx.ftp.file.handler"].process_ftp_files()

    @api.constrains("args")
    def _check_args(self):
        for record in self:
            try:
                self.str2tuple(record.args)
            except Exception as e:
                raise ValidationError(_("Invalid arguments: %s") % (record.args,)) from e
        return True

    @api.constrains("model_name", "method_name")
    def check_method(self):
        for record in self:
            if record.model_name or record.method_name:
                model = record.env[record.model_name]
                if record.method_name and not hasattr(model, record.method_name):
                    raise ValidationError(
                        _(
                            "Method '{methode_name}' does not exist " "in model '{model_name}'!"
                        ).format(
                            methode_name=record.method_name,
                            model_name=record.model_name,
                        )
                    )
        return True

    def check_directories(self, ftp_connection):
        if self.active:
            directory = os.path.join(self.ftp_connection_id.ftp_base, self.name)
            self.ftp_connection_id.check_ftp_directory(ftp_connection, directory)
            self.check_local_directory()

    def get_local_directory(self):
        if self.data_dir_prefix:
            data_dir = config.filestore(self._cr.dbname)
            return os.path.join(data_dir, self.local_directory)
        return self.local_directory

    def check_local_directory(self, directory=False):
        try:
            if directory:
                local_dir = directory
            else:
                local_dir = self.get_local_directory()

            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            if not os.path.exists(self.get_archive_dir(local_dir)):
                os.makedirs(self.get_archive_dir(local_dir))
            if (
                not os.path.exists(self.get_error_dir(local_dir))
                and self.direction == GET_DIRECTION
            ):
                os.makedirs(self.get_error_dir(local_dir))
        except Exception as e:
            raise ValidationError(
                _("Check local directory '{loc_directory}'\n{traceback}").format(
                    loc_directory=self.get_local_directory(),
                    traceback=traceback.format_exc(),
                )
            ) from e

    def get_archive_dir(self, directory=False):
        if directory:
            return os.path.join(directory, ARCHIVE_DIR)
        return os.path.join(self.get_local_directory(), ARCHIVE_DIR)

    def get_error_dir(self, directory=False):
        if directory:
            return os.path.join(directory, ERROR_DIR)
        return os.path.join(self.get_local_directory(), ERROR_DIR)

    def set_next_execution_date(self):
        now = fields.Datetime.context_timestamp(self, datetime.now())
        next_execution_date = fields.Datetime.context_timestamp(self, self.next_execution_date)
        while next_execution_date < now:
            next_execution_date += _intervalTypes[self.interval_type](self.interval_number)
        self.env.cr.execute(
            """UPDATE xx_ftp_connection_directory
                        SET next_execution_date = %s
                      WHERE id=%s""",
            (
                next_execution_date.astimezone(pytz.UTC).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                self.id,
            ),
        )

    def get_files_subdirs(self):
        ftp_connection = self.ftp_connection_id.get_connection()
        try:
            files = sorted(
                f
                for f in self.ftp_connection_id.list_dir(ftp_connection, self.name)
                if fnmatch.fnmatch(f, self.file_mask)
            )
            for file in files:
                path = os.path.join(self.name, file)
                is_dir = False
                try:
                    ftp_connection.size(path)
                except Exception:
                    is_dir = True
                if is_dir and file not in self.exclude_dirs.split(","):
                    self.get_files(file)
        finally:
            self.ftp_connection_id._close_ftp_connection(ftp_connection)

    # pylint: disable=E8102
    def get_files(self, subdir=False):  # noqa: C901
        ftp_connection = self.ftp_connection_id.get_connection()
        try:
            archive_dir = self.archive_name
            remote_dir = self.name
            if subdir:
                remote_dir = os.path.join(self.name, subdir)
            files = sorted(
                f
                for f in self.ftp_connection_id.list_dir(ftp_connection, remote_dir)
                if fnmatch.fnmatch(f, self.file_mask)
            )
        finally:
            self.ftp_connection_id._close_ftp_connection(ftp_connection)
        for file in files:
            self._try_lock()
            # Got the lock on the directory row, run its code
            self.get_logger().info("Processing file `%s`." % file)
            remote_file = os.path.join(remote_dir, file)
            ftp_connection = self.ftp_connection_id.get_connection()
            try:
                # set type to binary
                if self.ftp_connection_id.ftp_protocol == FTP_PROTOCOL:
                    ftp_connection.voidcmd("TYPE I")
                # size raises error if file is a directory, and returns -1 if file doesn't exist
                size = -1
                directory = False
                try:
                    if self.ftp_connection_id.ftp_protocol == FTP_PROTOCOL:
                        size = ftp_connection.size(remote_file)
                    elif self.ftp_connection_id.ftp_protocol == SFTP_PROTOCOL:
                        file_info = ftp_connection.lstat(remote_file)
                        if stat.S_ISDIR(file_info.st_mode):
                            size = -1
                            directory = True
                        else:
                            size = file_info.st_size
                except Exception:
                    directory = True
                if not directory and size != -1:
                    local_dir = self.get_local_directory()
                    if subdir:
                        local_dir = os.path.join(local_dir, subdir)
                    # check if local dir exist
                    self.check_local_directory(local_dir)
                    local_file = os.path.join(local_dir, file)
                    file_handler_values = {
                        "filename": local_file,
                        "ftp_connection_directory_id": self.id,
                    }
                    file_handler = self.env["xx.ftp.file.handler"].create(file_handler_values)
                    self.ftp_connection_id.get_file(ftp_connection, remote_file, local_file)
                    if self.attach_file:
                        with open(local_file, "rb") as rfile:
                            attachment = {
                                "name": os.path.basename(local_file),
                                "datas": base64.encodebytes(rfile.read()),
                                "store_fname": local_file,
                                "res_model": "xx.ftp.file.handler",
                                "res_id": file_handler.id,
                            }
                            try:
                                self.env["ir.attachment"].create(attachment)
                            except AccessError:
                                self.get_logger().warning("Cannot save the as attachment")
                            else:
                                self.get_logger().info("The file is now saved as attachment")
                    self._commit()
                    if self.archive_name:
                        try:
                            archive_remote_file = os.path.join(archive_dir, file)
                            if self.ftp_connection_id.ftp_protocol == FTP_PROTOCOL:
                                ftp_connection.rename(remote_file, archive_remote_file)
                            elif self.ftp_connection_id.ftp_protocol == SFTP_PROTOCOL:
                                ftp_connection.rename(remote_file, archive_remote_file)
                            self.get_logger().info(
                                f"The file {remote_file} is now archived to {archive_remote_file}"
                            )
                        except Exception:
                            self.get_logger().info("Remote file is already gone")
                    else:
                        try:
                            if self.ftp_connection_id.ftp_protocol == FTP_PROTOCOL:
                                ftp_connection.delete(remote_file)
                            elif self.ftp_connection_id.ftp_protocol == SFTP_PROTOCOL:
                                if ftp_connection.stat(remote_file):
                                    ftp_connection.remove(remote_file)
                        except Exception:
                            self.get_logger().info("Remote file is already gone")
            except Exception:
                self.get_logger().info("Import failed with exception: %s" % traceback.format_exc())
                self._rollback()
            finally:
                self.ftp_connection_id._close_ftp_connection(ftp_connection)

    def put_files_subdirs(self):
        ftp_connection = self.ftp_connection_id.get_connection()
        try:
            local_dir = self.get_local_directory()
            os.chdir(local_dir)
            dirs = sorted(f for f in glob.glob("*") if os.path.isdir(os.path.join(local_dir, f)))
            for directory in dirs:
                if directory not in self.exclude_dirs.split(","):
                    try:
                        self.ftp_connection_id.change_ftp_directory(
                            ftp_connection, os.path.join(self.name, directory)
                        )
                    except Exception:
                        ftp_connection.mkdir(os.path.join(self.name, directory))
                    self.put_files(directory)
        finally:
            self.ftp_connection_id._close_ftp_connection(ftp_connection)

    def put_files(self, subdir=False):
        local_dir = self.get_local_directory()
        if subdir:
            local_dir = os.path.join(local_dir, subdir)
        os.chdir(local_dir)
        files = sorted(
            f for f in glob.glob(self.file_mask) if os.path.isfile(os.path.join(local_dir, f))
        )
        for file in files:
            ftp_connection = self.ftp_connection_id.get_connection()
            try:
                local_file = os.path.join(local_dir, file)
                remote_dir = self.name
                if subdir:
                    remote_dir = os.path.join(remote_dir, subdir)
                remote_file = os.path.join(remote_dir, file)
                self.ftp_connection_id.put_file(
                    ftp_connection, local_file, remote_file, self.confirm_file_size
                )
                archive_dir = self.get_archive_dir()
                if subdir:
                    archive_dir = self.get_archive_dir(local_dir)
                    if not os.path.exists(archive_dir):
                        os.makedirs(archive_dir)
                archive_file = os.path.join(archive_dir, file)
                self.get_logger().info(f"Archiving file {local_file} to {archive_file}")
                os.rename(local_file, archive_file)
                self._callback()
            finally:
                self.ftp_connection_id._close_ftp_connection(ftp_connection)

    def process_directory(self):
        try:
            self._try_lock()
            # Got the lock on the directory row, run its code
            self.get_logger().debug("Processing directory `%s`." % self.name)
            try:
                # Process a given directory taking care of the repetition.
                if self.direction == GET_DIRECTION:
                    self.get_files()
                    if self.include_subdirs:
                        self.get_files_subdirs()
                elif self.direction == PUT_DIRECTION:
                    self.put_files()
                    if self.include_subdirs:
                        self.put_files_subdirs()
                else:
                    raise ValidationError(
                        _("process_directory not implemented for '%s'") % (self.direction,)
                    )
                if not self.env.context.get("called_from_button", False):
                    self.with_user(SUPERUSER_ID).invalidate_recordset()
                    self.set_next_execution_date()

                self._commit()
                self.get_logger().debug("Processed directory `%s`." % self.name)
            except Exception:
                self._rollback()
                self.get_logger().exception(
                    _("Unexpected exception while processing directory {name}\n{traceback}").format(
                        name=self.name,
                        traceback=traceback.format_exc(),
                    )
                )
        finally:
            pass
