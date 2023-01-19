# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    weight_move_total = fields.Float(
        default=0.0,
        compute="_compute_total_move_weight",
        store=True)

    weight_move_line_total = fields.Float(
        default=0.0,
        compute="_compute_total_move_line_weight",
        store=True)

    @api.depends("move_ids_without_package")
    def _compute_total_move_weight(self):
        for line in self:
            line.weight_move_total = sum(line.move_ids_without_package.mapped('weight_total'))

    @api.depends("move_line_ids_without_package")
    def _compute_total_move_line_weight(self):
        for line in self:
            line.weight_move_line_total = sum(line.move_line_ids_without_package.mapped('weight_total'))
