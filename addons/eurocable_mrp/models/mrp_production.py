from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    xx_weight = fields.Float(string="Weight", compute="_compute_total_weight", store=True)
    xx_product_description_variants = fields.Text("Custom Description")

    @api.depends("move_raw_ids.xx_weight", "origin")
    def _compute_total_weight(self):
        for rec in self:
            rec.xx_weight = 0
            for move in rec.move_raw_ids:
                rec.xx_weight += move.xx_weight

            sale_order = self.env["sale.order"].search([("name", "=", rec.origin)])
            for line in sale_order.order_line:
                line._compute_weight()
