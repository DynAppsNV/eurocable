from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move.line"

    weight = fields.Float(default=0.0)
