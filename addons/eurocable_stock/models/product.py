# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_description_sale_zpl(self):
        description_zpl = self.description_sale
        if description_zpl:
            print(description_zpl)
            description_zpl = description_zpl.replace('\n', '\&')
            print(description_zpl)
        return description_zpl
