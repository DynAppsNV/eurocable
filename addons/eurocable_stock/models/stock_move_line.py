from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange("product_id", "product_uom_id")
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        if self.product_id and self.picking_id:
            product = self.product_id.with_context(
                lang=self.picking_id.partner_id.lang or self.env.user.lang
            )
            self.description_picking = product.get_product_multiline_description_sale()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        move_lines = super().create(vals_list)
        for move_line in move_lines:
            if move_line.move_id:
                move_line.description_picking = move_line.move_id.description_picking
        return move_lines
