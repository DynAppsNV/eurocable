# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.stock.models import stock_move


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    priority = fields.Selection(stock_move.PROCUREMENT_PRIORITIES, default="0")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    priority = fields.Selection(
        stock_move.PROCUREMENT_PRIORITIES,
        compute="_compute_priority",
        inverse="_inverse_priority",
        store=True,
        index=True,
        tracking=True,
        help="Priority for this sale order. "
        "Setting manually a value here would set it as priority "
        "for all the order lines",
    )

    @api.depends("order_line.priority")
    def _compute_priority(self):
        for order in self.filtered(lambda x: x.order_line):
            priority = order.mapped("order_line.priority")
            order.priority = max([x for x in priority if x] or "0")

    def _inverse_priority(self):
        for order in self:
            priority = order.priority
            for line in order.order_line.filtered(
                lambda x, pr=priority: x.priority != pr
            ):
                line.priority = priority

    def action_confirm(self):
        return super(
            SaleOrder, self.with_context(sale_priority=self.priority)
        ).action_confirm()
