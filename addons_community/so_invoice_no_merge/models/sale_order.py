# -*- coding: utf-8 -*-

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        if self._context.get('flag_merge_invoices'):
            grouped = self._context.get('flag_merge_invoices')
        return super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)
