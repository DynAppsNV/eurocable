from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    date_terms_signed = fields.Datetime(help="Date on witch the sales conditions/terms are signed")
    print_terms = fields.Boolean(
        help="If true the sales conditions/terms will be printed on the documents", default=True
    )
