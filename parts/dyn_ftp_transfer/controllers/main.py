import os

from odoo import http
from odoo.http import content_disposition, request


class FtpFileViewer(http.Controller):
    @http.route("/dyn_interface_file/<rec_id>", type="http", auth="user")
    def dyn_interface_file(self, rec_id, **post):
        # prevent direct url access from users that don't have the right group
        if (
            request.env["res.users"]
            .browse(request.session.uid)
            .user_has_groups("dyn_ftp_transfer.group_interface_manager")
        ):
            filename = request.env["xx.ftp.file.handler"].browse(rec_id).filename
            if os.path.exists(filename):
                with open(filename) as file_data:
                    content = []
                    for line in file_data:
                        content += line
                    headers = [
                        ("Content-Type", "text/plain"),
                        (
                            "Content-Disposition",
                            content_disposition(os.path.split(filename)[1]),
                        ),
                    ]
                    response = request.make_response(content, headers=headers)
                    return response
        return False
