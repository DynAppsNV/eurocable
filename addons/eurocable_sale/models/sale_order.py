# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        show_warning = self._context.get('show_warning', False)
        if not self.partner_id.vat and not show_warning:
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
