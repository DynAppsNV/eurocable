# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    mrp_lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number',
                                 domain="[('product_id', '=', product_id)]")
