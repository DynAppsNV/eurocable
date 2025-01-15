from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    to_check = fields.Boolean(default=lambda self: self._default_to_check())

    def _default_to_check(self):
        return self._context.get("default_move_type") in ["in_refund", "in_invoice", "out_refund"]
