# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    weight_move = fields.Float(
        related='sale_id.weight_total',
        store=True)
