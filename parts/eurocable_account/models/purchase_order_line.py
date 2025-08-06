from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    xx_weight = fields.Float(string="Weight", compute="_compute_weight", store=True, readonly=False)

    @api.depends("product_id.weight")
    def _compute_weight(self):
        for line in self:
            line.xx_weight = 0
            if line.product_id:
                line.xx_weight = line.product_id.weight
