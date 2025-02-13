from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from odoo.addons.sale.tests.common import TestSaleCommon
from odoo.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_common import (
    ValuationReconciliationTestCommon,
)


@tagged("post_install", "-at_install")
class TestDeliveryDateOnPicking(TestSaleCommon, ValuationReconciliationTestCommon):
    def setUp(self):
        super().setUp()
        self.so_commitment_datetime = fields.datetime.now() + timedelta(hours=1)

        self.partner_a.vat = "SOME VAT NUMBER"
        self.so = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "partner_invoice_id": self.partner_a.id,
                "partner_shipping_id": self.partner_a.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                    for p in (
                        self.company_data["product_order_no"],
                        self.company_data["product_service_delivery"],
                        self.company_data["product_service_order"],
                        self.company_data["product_delivery_no"],
                    )
                ],
                "pricelist_id": self.company_data["default_pricelist"].id,
                "picking_policy": "direct",
                "commitment_date": self.so_commitment_datetime,
            }
        )

    def test_01_delivery_date_on_picking(self):
        self.so.action_confirm()

        self.assertTrue(self.so.picking_ids)
        picking = self.so.picking_ids[0]
        self.assertEqual(picking.date_done, self.so_commitment_datetime)
        self.assertEqual(picking.scheduled_date, self.so_commitment_datetime)
