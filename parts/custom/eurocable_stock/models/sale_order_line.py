from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_description_sale_zpl(self):
        description_zpl = self.name
        if description_zpl:
            description_zpl = description_zpl.replace("\n", r"\&")  # NOQA
        return description_zpl
