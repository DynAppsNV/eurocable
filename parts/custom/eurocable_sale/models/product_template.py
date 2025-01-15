from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    document_type_id = fields.Many2one("document.type")
