from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    xx_use_one_time_delivery_address = fields.Boolean(string="Use One Time Delivery Address")
    xx_one_time_delivery_address = fields.Text(string="One Time Delivery Address")
