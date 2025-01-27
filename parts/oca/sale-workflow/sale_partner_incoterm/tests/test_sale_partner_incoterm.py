# Copyright 2015 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form, TransactionCase


class TestSalePartnerIncoterm(TransactionCase):
    def test_sale_partner_incoterm(self):
        """
        Check that the customer's default incoterm is retrieved in the
        sales order's onchange
        """
        customer = self.env.ref("base.res_partner_3")
        incoterm = self.env["account.incoterms"].search([], limit=1)
        address = self.env["res.partner"].search([], limit=1)
        customer.write(
            {"sale_incoterm_id": incoterm.id, "sale_incoterm_address_id": address.id}
        )
        sale_order = Form(self.env["sale.order"])
        sale_order.partner_id = customer
        self.assertEqual(sale_order.incoterm, incoterm)
        self.assertEqual(sale_order.incoterm_address_id, address)
