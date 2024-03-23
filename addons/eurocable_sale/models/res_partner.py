from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    ref = fields.Char()
    is_not_vat = fields.Boolean(string="Not VAT Obligated")
