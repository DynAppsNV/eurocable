# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_description_sale_zpl(self):
        description_zpl = self.name
        if description_zpl:
            description_zpl = description_zpl.replace('\n', '\&') # NOQA
        return description_zpl
