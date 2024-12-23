from odoo import fields, models


class AccountInvoiceExtractionWords(models.Model):
    _inherit = "account_invoice_extract.account.invoice_extract.words"

    invoice_id = fields.Many2one(required=False)
