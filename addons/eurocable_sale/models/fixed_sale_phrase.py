from odoo import fields, models


class FixedSalePhrase(models.Model):
    _name = "xx.fixed.sale.phrase"
    _description = "Fixed Sale Phrase which can be added to the Sale Order as a note"

    name = fields.Char(required=True)
    phrase = fields.Text(required=True)
