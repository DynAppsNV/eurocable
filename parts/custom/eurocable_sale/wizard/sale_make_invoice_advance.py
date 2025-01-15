from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def get_sale_id(self):
        if self._context.get("active_model") == "sale.order" and self._context.get(
            "active_id", False
        ):
            sale_orders = self.env["sale.order"].browse(self._context.get("active_ids"))
            if sale_orders:
                return sale_orders

    def _is_message_exists(self):
        sale_ids = self.get_sale_id()
        if not sale_ids:
            return False
        if any(sale_ids.partner_invoice_id.filtered(lambda x: x.invoice_warn_msg)):
            return True
        else:
            return False

    def _get_message(self):
        sale_orders = self.get_sale_id()
        if not sale_orders:
            return ""
        if len(sale_orders) > 1:
            message = ""
            for order in sale_orders:
                if order.partner_invoice_id.invoice_warn_msg:
                    message += (
                        order.partner_invoice_id.display_name
                        + "\n"
                        + order.partner_invoice_id.invoice_warn_msg
                        + "\n"
                    )
            return message
        else:
            if sale_orders.partner_invoice_id.invoice_warn_msg:
                return sale_orders.partner_invoice_id.invoice_warn_msg

    is_warn_message = fields.Boolean("Is Warning Message", default=_is_message_exists)
    warn_message = fields.Text("Message", default=_get_message)
