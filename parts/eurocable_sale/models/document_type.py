from odoo import fields, models


class DocumentType(models.Model):
    _name = "document.type"
    _description = "Type Document"

    name = fields.Char(required=True)
    text = fields.Html(translate=True)
    company_id = fields.Many2one(
        "res.company",
        help="Leave empty to share this certification with all companies.",
    )
