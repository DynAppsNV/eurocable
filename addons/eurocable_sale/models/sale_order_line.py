from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    document_type = fields.Many2one(related="product_id.document_type_id")
    has_certificate = fields.Boolean(default=False)
    certificate_notes = fields.Text()
