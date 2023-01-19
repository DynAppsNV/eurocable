# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.onchange('product_id', 'picking_type_id')
    def _onchange_product_id(self):
        res = super(StockMove, self)._onchange_product_id()
        product = self.product_id.with_context(lang=self._get_lang())
        if product:
            self.description_picking = product.get_product_multiline_description_sale()
        return res

    @api.model
    def create(self, vals):
        res = super(StockMove, self).create(vals)
        if res.sale_line_id:
            res.description_picking = res.sale_line_id.name
        return res
