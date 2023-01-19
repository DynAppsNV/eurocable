# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

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
        "product_uom_qty",
        "weight")
    def _compute_total_weight(self):
        for rec in self:
            if rec.weight:
                rec.weight_total = rec.weight * rec.product_uom_qty

    @api.onchange('product_id', 'picking_type_id')
    def _onchange_product_id(self):
        super(StockMove, self)._onchange_product_id()
        product = self.product_id.with_context(lang=self._get_lang())
        if product:
            self.description_picking = product.get_product_multiline_description_sale()

    @api.model
    def create(self, vals):
        res = super(StockMove, self).create(vals)
        if res.sale_line_id:
            res.description_picking = res.sale_line_id.name
        return res
