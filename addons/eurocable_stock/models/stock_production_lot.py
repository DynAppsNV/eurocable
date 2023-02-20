# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    def name_get(self):
        result = []
        for lot in self:
            name = lot.name + ' ' + '(' + str(lot.product_qty) + ' ' + str(lot.product_uom_id.name)\
                     + ')'
            result.append((lot.id, name))
        return result
