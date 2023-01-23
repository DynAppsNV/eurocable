# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    document_type = fields.Many2one(related='product_id.document_type_id')
    has_certificate = fields.Boolean(default=False)
    certificate_notes = fields.Text()
    weight = fields.Float(default=0.0)
    weight_total = fields.Float(
        default=0.0,
        compute="_compute_total_weight")

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.weight = self.product_id.weight
        return res

    @api.depends(
        "product_template_id",
        "product_id",
        "product_uom_qty",
        "weight")
    def _compute_total_weight(self):
        for rec in self:
            rec.weight_total = 0.0
            if rec.weight:
                rec.weight_total = rec.weight * rec.product_uom_qty
