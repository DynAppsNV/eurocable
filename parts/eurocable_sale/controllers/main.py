from odoo import _, http
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
            return request.make_response(
                _("There are no certificates for this order."),
                headers=[("Content-Type", "text/plain; charset=utf-8")],
                status=404,
            )
        return request.make_response(
            pdf,
            headers=[
                ("Content-Type", "application/pdf"),
                ("Content-Length", len(pdf)),
                ("Content-Disposition", content_disposition(f"Certificates_{order.name}.pdf")),
            ],
        )
