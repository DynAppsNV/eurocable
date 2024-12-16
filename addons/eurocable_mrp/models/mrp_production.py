from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    xx_weight = fields.Float(string="Weight per Unit", compute="_compute_weight", store=True)
    xx_product_description_variants = fields.Text("Custom Description")

    @api.depends("move_raw_ids.xx_weight", "origin", "product_qty")
    def _compute_weight(self):
        for rec in self:
            weight = 0
            for move in rec.move_raw_ids:
                weight += move.xx_weight
            rec.xx_weight = weight / rec.product_qty

            sale_order = self.env["sale.order"].search([("name", "=", rec.origin)])
            for line in sale_order.order_line:
                line._compute_weight()
