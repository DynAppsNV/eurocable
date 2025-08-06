from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    ref = fields.Char()
    is_not_vat = fields.Boolean(string="Not VAT Obligated")
