# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    is_weight = fields.Boolean(
        help="When checked, the weight will be included in the invoice")
