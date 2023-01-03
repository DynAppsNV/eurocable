# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    document_type = fields.Many2one(related='product_id.document_type_id')
    has_certificate = fields.Boolean(default=False)
    certificate_notes = fields.Text()
