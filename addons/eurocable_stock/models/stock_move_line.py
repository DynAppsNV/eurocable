# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    weight = fields.Float(default=0.0)
    weight_total = fields.Float(
        default=0.0,
        compute="_compute_total_weight",
        store=True)

    @api.onchange("product_id")
    def _onchange_weight(self):
        if self.product_id:
            self.weight = self.product_id.weight

    @api.depends(
        "product_id",
        "qty_done",
        "weight")
    def _compute_total_weight(self):
        for rec in self:
            if rec.weight:
                rec.weight_total = rec.weight * rec.qty_done

    @api.onchange('product_id', 'product_uom_id')
    def _onchange_product_id(self):
        res = super(StockMoveLine, self)._onchange_product_id()
        if self.product_id and self.picking_id:
            product = self.product_id.with_context(lang=self.picking_id.partner_id.lang or self.env.user.lang)
            self.description_picking = product.get_product_multiline_description_sale()
        return res

    @api.model
    def create(self, vals):
        res = super(StockMoveLine, self).create(vals)
        if res.move_id:
            res.description_picking = res.move_id.description_picking
        return res
