# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model_create_multi
    def create(self, vals_list):
        new_records = super(IrAttachment, self).create(vals_list)
        for record in new_records.\
                filtered(lambda x: x.res_model == 'sale.order'):
            sale_order_id = self.env['sale.order'].\
                search([('id', '=', record.res_id)])
            if sale_order_id and 'copy_po_att' not in self._context:
                record.with_context({'copy_po_att': True}).sudo().copy()
            if 'copy_po_att' in self._context and 'copy_del_att' \
                    not in self._context:
                sale_order_id.sudo().\
                    write({'sale_po_attachment_ids': [(4, record.id)]})
            if sale_order_id and 'copy_po_att' in self._context and\
                    'copy_del_att' not in self._context:
                record.with_context({'copy_po_att': True,
                                     'copy_del_att': True}).sudo().copy()
            if 'copy_del_att' in self._context:
                sale_order_id.sudo().\
                    write({'sale_delivery_attachment_ids': [(4, record.id)]})
        return new_records
