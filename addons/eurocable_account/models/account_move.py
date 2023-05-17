# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, api, _
from odoo.exceptions import UserError


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

    # Override method to remove is_move_sent checkbox from updating
    def button_draft(self):
        AccountMoveLine = self.env['account.move.line']
        excluded_move_ids = []

        if self._context.get('suspense_moves_mode'):
            excluded_move_ids = AccountMoveLine.\
                search(AccountMoveLine._get_suspense_moves_domain() +
                       [('move_id', 'in', self.ids)]).mapped('move_id').ids

        for move in self:
            if move in move.line_ids.\
                    mapped('full_reconcile_id.exchange_move_id'):
                raise UserError(_('You cannot reset to '
                                  'draft an exchange difference journal '
                                  'entry.'))
            if move.tax_cash_basis_rec_id or\
                    move.tax_cash_basis_origin_move_id:
                # If the reconciliation was undone,
                # move.tax_cash_basis_rec_id will be empty;
                # but we still don't want to allow setting the caba entry
                # to draft
                # (it'll have been reversed automatically, so no manual
                # intervention is required),
                # so we also check tax_cash_basis_origin_move_id, which
                # stays unchanged
                # (we need both, as tax_cash_basis_origin_move_id did not
                # exist in older versions).
                raise UserError(_('You cannot reset to draft a tax cash'
                                  ' basis journal entry.'))
            if move.restrict_mode_hash_table and move.state == 'posted'\
                    and move.id not in excluded_move_ids:
                raise UserError(_('You cannot modify a posted entry of this'
                                  ' journal because it is in strict mode.'))
            # We remove all the analytics entries for this journal
            move.mapped('line_ids.analytic_line_ids').unlink()

        self.mapped('line_ids').remove_move_reconcile()
        self.write({'state': 'draft'})
