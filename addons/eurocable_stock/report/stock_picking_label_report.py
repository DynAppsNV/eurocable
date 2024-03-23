from collections import defaultdict

from odoo import models


class ReportStockPickingLabel(models.AbstractModel):
    _name = "report.eurocable_stock.green_card_label"
    _description = "Stock Picking Label Report"

    def _get_report_values(self, docids, data):
        MoveLine = self.env["stock.move.line"]
        quantity_by_product = defaultdict(list)
        for p, q in data.get("quantity_by_product").items():
            move_line = MoveLine.browse(int(p))
            quantity_by_product[move_line].append((move_line.product_id, q))
        data["quantity"] = quantity_by_product

        return data
