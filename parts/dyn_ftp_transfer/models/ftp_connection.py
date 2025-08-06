from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.job import identity_exact


class FtpConnection(models.Model):
    _inherit = "xx.ftp.connection"

    ftp_directory_ids = fields.One2many(
        comodel_name="xx.ftp.connection.directory",
        inverse_name="ftp_connection_id",
        string="FTP Directories",
    )

    def _test_connection_hook(self, ftp_connection):
        super()._test_connection_hook(ftp_connection)
        if not self.ftp_directory_ids:
            raise ValidationError(_("Please define some directories!"))
        for ftp_directory in self.ftp_directory_ids:
            ftp_directory.check_directories(ftp_connection)
        return True

    @api.model
    def process_ftp_connections(self):
        self.env["xx.ftp.connection"].flush_model()
        self.env["xx.ftp.connection.directory"].flush_model()
        self.env.cr.execute(
            """
            SELECT xfcd.*
              FROM xx_ftp_connection_directory xfcd
                   INNER JOIN xx_ftp_connection xfc on xfc.id = xfcd.ftp_connection_id
                                                   and xfc.active
                                                   and xfc.state = 'confirm'
             WHERE 1=1
               AND xfcd.active
               AND xfcd.next_execution_date <= (now() AT TIME ZONE 'UTC')
             ORDER
                BY xfcd.priority
            """
        )
        for directory in self.env.cr.dictfetchall():
            ftp_dir = self.env["xx.ftp.connection.directory"].browse(directory["id"])
            ftp_dir.with_delay(
                priority=20,
                max_retries=5,
                channel=self.env.ref("dyn_ftp_transfer.channel_ftp_connections_queue").name,
                description="FTP Connection Job",
                identity_key=identity_exact,
            ).process_directory()
