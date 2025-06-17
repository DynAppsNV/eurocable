from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    xx_weight = fields.Float(string="Weight", compute="_compute_weight")

    def _compute_weight(self):
        for rec in self:
            production = self.env["mrp.production"].search(
                [("lot_producing_id", "=", rec.id)], limit=1
            )
            rec.xx_weight = production.xx_weight
