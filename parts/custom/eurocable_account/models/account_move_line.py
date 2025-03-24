from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    weight = fields.Float(compute="_compute_weight", store=True, readonly=False)

    @api.depends("sale_line_ids.weight", "purchase_line_id.product_id.weight")
    def _compute_weight(self):
        for move in self:
            move.weight = 0
            if move.sale_line_ids:
                move.weight = move.sale_line_ids.weight
            elif move.purchase_line_id and move.purchase_line_id.product_id:
                move.weight = move.purchase_line_id.product_id.weight
