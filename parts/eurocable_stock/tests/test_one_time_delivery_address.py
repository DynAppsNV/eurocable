from odoo import Command
from odoo.tests import tagged

from odoo.addons.sale.tests.common import TestSaleCommon


@tagged("post_install", "-at_install")
class TestDeliveryDateOnPicking(TestSaleCommon):
    def setUp(self):
        super().setUp()

        self.partner_a.vat = "SOME VAT NUMBER"
        self.so = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "partner_invoice_id": self.partner_a.id,
                "partner_shipping_id": self.partner_a.id,
                "xx_one_time_delivery_address": "TEST ADDRESS",
                "xx_use_one_time_delivery_address": True,
                "order_line": [
                    Command.create(
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        }
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
            }
        )

    def test_01_one_time_delivery_address_on_picking(self):
        self.so.action_confirm()
        self.assertEqual(self.so.picking_ids.xx_one_time_delivery_address, "TEST ADDRESS")

    def test_02_one_time_delivery_address_not_on_picking(self):
        self.so.xx_use_one_time_delivery_address = False
        self.so.action_confirm()
        self.assertFalse(self.so.picking_ids.xx_one_time_delivery_address)
