# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Attachment related fields
    sale_po_attachment_ids = fields.Many2many('ir.attachment',
                                              'sale_purchase_order_document_rel',
                                              string='Purchase '
                                                     'Documents', copy=False)
    sale_delivery_attachment_ids = fields.Many2many('ir.attachment',
                                                    'sale_transfer_document_rel',
                                                    string='Delivery '
                                                           'Documents',
                                                    copy=False)
    sale_send_so_to_inv = fields.Boolean(related='partner_id.send_so_to_inv')
    is_attach_purchase_docs = fields.Boolean('Attach Purchase Documents?',
                                             copy=False,
                                             help="If this checkbox is marked"
                                                  " then all Purchase "
                                                  "Documents will attached in"
                                                  " Invoice's email.")
    is_attach_delivery_note = fields.Boolean('Attach Delivery Notes?',
                                             copy=False,
                                             help="If this checkbox is "
                                                  "marked then all the "
                                                  "Delivery documents will"
                                                  " attached in Invoice's"
                                                  " email.")
