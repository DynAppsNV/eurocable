from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move.line"

    weight = fields.Float(related="sale_line_ids.weight", store=True, readonly=False)
