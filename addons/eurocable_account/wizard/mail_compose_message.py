# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, api


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    # Over-ride function to add sales attachment in existing values
    # Based on context do the changes
    # Return : If conditions full-filled, add the attachment
    @api.onchange('template_id')
    def _onchange_template_id_wrapper(self):
        self.ensure_one()
        values = self._onchange_template_id(self.template_id.id,
                                            self.composition_mode, self.model,
                                            self.res_id)['value']

        invoice = self._context.get('invoice_sale_attachment')
        # Based on context found, do the process
        if invoice:
            sale_attachment = False
            if invoice.invoice_line_ids and \
                    invoice.invoice_line_ids.sale_line_ids:
                # One invoice will be linked to one sale order
                sale_order = invoice.invoice_line_ids.\
                    sale_line_ids.mapped('order_id')
                if sale_order:
                    # Take the 1st attachment from linked sale order
                    sale_attachment = self.env['ir.attachment'].search([
                        ('res_model', '=', 'sale.order'),
                        ('res_id', '=', sale_order.id)])[0]
            # Add attachment to existing attachments
            values['attachment_ids'] = [(6, 0,
                                         (values.get('attachment_ids')[0][-1]
                                          + [sale_attachment.id]))]

        for fname, value in values.items():
            setattr(self, fname, value)
