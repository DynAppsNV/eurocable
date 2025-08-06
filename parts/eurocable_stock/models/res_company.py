from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    logo_zpl = fields.Text(
        string="Logo ZPL", help="Encoded string of logo used in ZPL report " "print."
    )
