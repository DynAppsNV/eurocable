from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    xx_product_attribute_group_ids = fields.One2many(
        "xx.product.attribute.group", "attribute_id", string="Attribute Groups"
    )


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    xx_product_attribute_group_id = fields.Many2one(
        "xx.product.attribute.group", string="Attribute Group"
    )

    xx_product_attribute_group_ids = fields.Many2many(
        "xx.product.attribute.group", compute="_compute_xx_product_attribute_group_ids"
    )

    def _compute_xx_product_attribute_group_ids(self):
        for record in self:
            record.xx_product_attribute_group_ids = (
                record.attribute_id.xx_product_attribute_group_ids
            )
