from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    weight = fields.Float(related="sale_line_id.weight")
    total_weight = fields.Float(compute="_compute_total_weight", default=0.0)

    @api.depends("product_id", "quantity", "weight")
    def _compute_total_weight(self):
        for rec in self:
            rec.total_weight = 0.0
            if rec.weight:
                rec.total_weight = rec.weight * rec.quantity

    @api.onchange("product_id", "picking_type_id")
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        product = self.product_id.with_context(lang=self._get_lang())
        if product:
            self.description_picking = product.get_product_multiline_description_sale()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        for move in moves:
            if move.sale_line_id:
                move.description_picking = move.sale_line_id.name
        return moves
