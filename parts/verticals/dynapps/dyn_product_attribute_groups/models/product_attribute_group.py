from odoo import fields, models


class ProductAttributeGroup(models.Model):
    _name = "xx.product.attribute.group"
    _description = "Product Attribute Group"

    name = fields.Char(translate=True, required=True)
    attribute_id = fields.Many2one("product.attribute", required=True)
