from odoo import models


class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    def name_get(self):
        result = []
        for lot in self:
            name = (
                lot.name
                + " "
                + "("
                + str(lot.product_qty)
                + " "
                + str(lot.product_uom_id.name)
                + ")"
            )
            result.append((lot.id, name))
        return result
