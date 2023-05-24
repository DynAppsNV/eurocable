# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, api, _
from odoo.exceptions import UserError


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
            sale_attachment = []
            if invoice.invoice_line_ids and \
                    invoice.invoice_line_ids.sale_line_ids:
                # One invoice will be linked to one sale order
                sale_order = invoice.invoice_line_ids.\
                    sale_line_ids.mapped('order_id')
                if sale_order:
                    # Take the attachments from linked sale order
                    if sale_order.partner_invoice_id and sale_order.\
                            partner_invoice_id.send_so_to_inv:
                        # Get value from sale order Purchase Documents
                        if sale_order.is_attach_purchase_docs:
                            for po_attachment in \
                                    sale_order.sale_po_attachment_ids:
                                sale_attachment.\
                                    append(po_attachment.id)
                        # Get value from sale order Delivery Documents
                        if sale_order.is_attach_delivery_note:
                            for delivery_attachment in \
                                    sale_order.sale_delivery_attachment_ids:
                                sale_attachment.\
                                    append(delivery_attachment.id)
                        # Raise error if there's no document found
                        if not sale_attachment:
                            raise UserError(_('There is no attachment found'
                                              ' in sale order. Link '
                                              'attachments before sending '
                                              'mail.'))
            # Add attachment to existing attachments
            values['attachment_ids'] = [(6, 0,
                                         (values.get('attachment_ids')[0][-1]
                                          + sale_attachment))]

        for fname, value in values.items():
            setattr(self, fname, value)
