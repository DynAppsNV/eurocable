from odoo import fields, models


class AccountInvoiceExtractionWords(models.Model):
    _name = "account.invoice_extract.words"

    invoice_id = fields.Many2one(required=False)
