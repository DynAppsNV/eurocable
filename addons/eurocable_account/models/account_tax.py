# Copyright 2023 Eezee-IT (<http://www.eezee-it.com> - admin@eezee-it.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    show_intrastat = fields.Boolean()
