from odoo import Command
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import float_compare


@tagged("post_install", "-at_install")
class TestWeight(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product_purchase = self.env["product.product"].create(
            {
                "name": "Purchase Test Product",
                # "categ_id": self.env.ref("product.product_category_all").id,
                "purchase_method": "purchase",
                "weight": 10,
            }
        )
        self.product_sale = self.env["product.product"].create(
            {
                "name": "Sale Test Product",
                # "categ_id": self.env.ref("product.product_category_all").id,
                "invoice_policy": "order",
                "weight": 20,
            }
        )
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

    def test_01_weight_on_sale(self):
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create({"product_id": self.product_sale.id, "product_uom_qty": 1})
                ],
            }
        )  # create sale order
        so.with_context(show_warning=True).action_confirm()
        so._create_invoices()
        self.assertTrue(so.invoice_ids)
        self.assertEqual(
            float_compare(
                so.invoice_ids.line_ids.filtered(
                    lambda li: li.product_id == self.product_sale
                ).weight,
                20,
                precision_digits=3,
            ),
            0,
        )

    def test_02_weight_on_lot(self):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_purchase.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        po.button_confirm()
        po.action_create_invoice()
        self.assertTrue(po.invoice_ids)
        self.assertEqual(
            float_compare(
                po.invoice_ids.line_ids.filtered(
                    lambda li: li.product_id == self.product_purchase
                ).weight,
                10,
                precision_digits=3,
            ),
            0,
        )
