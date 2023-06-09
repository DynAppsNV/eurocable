# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, api, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    # Calculate weight base on conditions
    def _calculate_weight(self, record):
        weight_sum = 0.0
        for line in record.bom_line_ids.filtered(lambda l:
                                                 l.product_id and
                                                 l.product_qty > 0.0):
            # Divide weight by qty to get per unit weight
            weight_sum += line.product_id.weight * line.product_qty

        # If we are creating BOM for more than 1 qty of finish product
        if record.product_qty != 0:
            weight_sum = weight_sum / record.product_qty

        # Check for product variant
        if record.product_tmpl_id and record.product_id:
            record.product_id.weight = weight_sum
        else:
            record.product_tmpl_id.weight = weight_sum

    # Calculate total weight of finish product
    @api.model
    def create(self, vals):
        res = super(MrpBom, self).create(vals)
        if res.bom_line_ids:
            self._calculate_weight(res)
        return res

    def write(self, vals):
        rec = super().write(vals)
        if 'product_qty' or 'product_tmpl_id' or 'product_id' or \
                'bom_line_ids' in vals:
            self._calculate_weight(self)
        return rec


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number',
                             domain="[('product_id', '=', product_id)]")
