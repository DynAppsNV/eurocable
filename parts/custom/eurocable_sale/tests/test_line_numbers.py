from odoo import Command
from odoo.tests import TransactionCase


class TestLineNumbers(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "order_line": [
                    Command.create(
                        {
                            "name": "Some Section",
                            "display_type": "line_section",
                        },
                    ),
                    Command.create(
                        {
                            "name": "Some Product",
                            "product_id": cls.env.ref("product.product_product_1").id,
                        },
                    ),
                    Command.create(
                        {
                            "name": "Some Other Product",
                            "product_id": cls.env.ref("product.product_product_2").id,
                        },
                    ),
                ]
                * 3,
            }
        )

    def test_line_numbers(self):
        """Test that the line numbers are computed correctly."""
        # Thrice a section line, a product line, and another product line
        self.assertListEqual(
            self.sale_order.order_line.mapped("xx_number"),
            [0, 10, 20, 0, 30, 40, 0, 50, 60],
        )
