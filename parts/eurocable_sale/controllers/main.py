from odoo import http
from odoo.http import content_disposition, request


class CertificateController(http.Controller):
    @http.route(
        "/eurocable_sale/certificates/<int:order_id>",
        type="http",
        auth="user",
    )
    def download_certificates(self, order_id):
        order = request.env["sale.order"].browse(order_id).exists()
        if not order:
            raise request.not_found()
        order.check_access_rights("read")
        order.check_access_rule("read")
        pdf = order._get_certificate_bundle_pdf()
        if not pdf:
            raise request.not_found()
        return request.make_response(
            pdf,
            headers=[
                ("Content-Type", "application/pdf"),
                ("Content-Length", len(pdf)),
                ("Content-Disposition", content_disposition(f"Certificates_{order.name}.pdf")),
            ],
        )
