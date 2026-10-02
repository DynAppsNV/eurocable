from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    xx_certificate_logo = fields.Image(
        string="Certificate Logo",
        max_width=1024,
        max_height=1024,
        help="Logo printed on top of the certificate. "
        "Leave empty to use the default Eurocable logo.",
    )
    xx_certificate_stamp = fields.Image(
        string="Certificate Stamp",
        max_width=1024,
        max_height=1024,
        help="Stamp or signature printed at the bottom of the certificate. "
        "Leave empty to use the default Eurocable stamp.",
    )
    xx_certificate_signatory = fields.Char(
        string="Certificate Signatory",
        help="Name printed under the stamp on the certificate. "
        "Leave empty to use the default Eurocable signatory.",
    )
