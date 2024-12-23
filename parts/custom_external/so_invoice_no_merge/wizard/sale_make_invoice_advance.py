from odoo import models, fields


class SaleAdvancePaymentInvInherit(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    merge_invoices = fields.Boolean(string="Merge Invoices", default=False)

    def create_invoices(self):
        if self.merge_invoices:
            return super(SaleAdvancePaymentInvInherit, self).create_invoices()
        else:
            return super(SaleAdvancePaymentInvInherit, self.with_context(flag_merge_invoices=True)).create_invoices()
