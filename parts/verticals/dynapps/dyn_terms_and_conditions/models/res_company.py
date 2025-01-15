from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    term_rule_ids = fields.One2many(
        comodel_name="term.rule", inverse_name="company_id", help="List of terms for this company."
    )
