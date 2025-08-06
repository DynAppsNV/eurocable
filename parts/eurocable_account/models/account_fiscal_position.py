from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    is_weight = fields.Boolean(help="When checked, the weight will be included in the invoice")
