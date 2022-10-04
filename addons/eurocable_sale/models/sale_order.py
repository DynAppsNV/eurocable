# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_discount = fields.Monetary(
        compute="_compute_total_discount",
        readonly=False,
    )
    total_prices = fields.Monetary(
        compute="_compute_total_prices",
        readonly=False,
    )

    @api.depends("order_line")
    def _compute_total_prices(self):
        total_price = 0
        for rec in self:
            for order in rec.order_line:
                total_price += order.price_unit * order.product_uom_qty
            rec.total_prices = total_price

    @api.depends("order_line")
    def _compute_total_discount(self):
        total_discount = 0
        for order in self.order_line:
            total_discount += (order.price_unit * order.product_uom_qty) * (order.discount / 100)
        self.total_discount = round(total_discount, 2)

    def action_confirm(self):
        show_warning = self._context.get('show_warning', False)
        if not self.partner_id.vat and not show_warning and not self.partner_id.is_not_vat:
            return {
                'name': 'Warning',
                'type': 'ir.actions.act_window',
                'res_model': 'sales.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {
                    'show_warning': True,
                }
            }
        return super(SaleOrder, self).action_confirm()
