# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for move in self:
            if move.move_type in ['in_invoice', 'in_refund']:
                move.to_check = True
        res = super(AccountMove, self).action_post()
        return res

    @api.model
    def _cron_show_in_intrastat(self):
        invoice_line_ids = self.env['account.move.line'].search([
            ('product_id.detailed_type', 'in', ['consu', 'product'])])
        if invoice_line_ids:
            invoice_line_ids.sudo().write({'show_in_report': True})
