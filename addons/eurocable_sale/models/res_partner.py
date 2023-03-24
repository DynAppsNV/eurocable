# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    email = fields.Char(required=True)
    ref = fields.Char()
    is_not_vat = fields.Boolean(string="Not VAT Obligated")
    send_so_to_inv = fields.Boolean('Send SO info with invoice', default=False,
                                    copy=False)
