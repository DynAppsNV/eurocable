# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, api, _, _lt

class ReportPartnerLedgerSuppliers(models.AbstractModel):
    _inherit = "account.partner.ledger"
    _name = "account.partner.ledger.suppliers"
    _description = "Partner Ledger Suppliers"

    filter_account_type = [
        {'id': 'payable', 'name': _lt('Suppliers'), 'selected': True},
    ]

    @api.model
    def _get_report_name(self):
        return _('Partner Ledger Suppliers')
