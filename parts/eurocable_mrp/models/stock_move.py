from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    xx_weight = fields.Float(string="Weight", compute="_compute_weight", store=True)

    @api.depends("product_id.weight", "product_uom_qty")
    def _compute_weight(self):
        for rec in self:
            rec.xx_weight = rec.product_id.weight * rec.product_uom_qty

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        res["sale_line_id"] = self.sale_line_id.id
        return res
