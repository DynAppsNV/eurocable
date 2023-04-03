# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, api


class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'

    # Over-ride function for adding context while template changes
    # Use context in mail.compose.message to add attachment
    @api.onchange('template_id')
    def onchange_template_id(self):
        for wizard in self:
            if wizard.composer_id:

                ctx = dict(self._context)
                # Only work when there is not mass-mail
                # Also customer have checkbox checked
                if not len(wizard.invoice_ids) > 1:
                    if wizard.invoice_ids.partner_id.send_so_to_inv:
                        ctx.update({'invoice_sale_attachment':
                                    self.invoice_ids[0]})

                wizard.composer_id.template_id = wizard.template_id.id
                wizard._compute_composition_mode()

                # Call method via context
                wizard.composer_id.with_context(ctx).\
                    _onchange_template_id_wrapper()

    # Over-ride function for adding context while mail checkbox change
    # Used context to add attachment from mail.compose.message
    @api.onchange('is_email')
    def onchange_is_email(self):
        if self.is_email:
            res_ids = self._context.get('active_ids')

            ctx = dict(self._context)
            # Only work when there is not mass-mail
            # Also customer have checkbox checked
            if not len(self.invoice_ids) > 1:
                if self.invoice_ids.partner_id.send_so_to_inv:
                    ctx.update({'invoice_sale_attachment':
                                self.invoice_ids[0]})

            if not self.composer_id:
                self.composer_id = self.env['mail.compose.message'].create({
                    'composition_mode': 'comment' if len(res_ids) == 1 else
                    'mass_mail',
                    'template_id': self.template_id.id})
            else:
                self.composer_id.composition_mode = 'comment' \
                    if len(res_ids) == 1 else 'mass_mail'
                self.composer_id.template_id = self.template_id.id
                self._compute_composition_mode()

            # Call method via context
            self.composer_id.with_context(ctx)._onchange_template_id_wrapper()
