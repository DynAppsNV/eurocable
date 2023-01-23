# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    weight_move = fields.Float(compute='_compute_total_weight',
                               default=0.0)

    @api.depends("move_ids_without_package")
    def _compute_total_weight(self):
        for line in self:
            line.weight_move = sum(line.move_ids_without_package.mapped('total_weight'))
