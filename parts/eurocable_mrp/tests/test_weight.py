from odoo import Command
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWeight(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "weight": 10,
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "weight": 20,
            }
        )
        cls.main_product = cls.env["product.product"].create(
            {
                "name": "Main Product",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )
        cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.main_product.product_tmpl_id.id,
                "product_qty": 1,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product1.id,
                            "product_qty": 1,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product2.id,
                            "product_qty": 2,
                        }
                    ),
                ],
            }
        )

    def test_01_weight_on_production(self):
        production = self.env["mrp.production"].create(
            {
                "product_id": self.main_product.id,
                "product_qty": 1,
            }
        )
        self.assertEqual(production.xx_weight, 50)

    def test_02_weight_on_lot(self):
        production = self.env["mrp.production"].create(
            {
                "product_id": self.main_product.id,
                "product_qty": 1,
            }
        )
        production.action_confirm()
        production.action_generate_serial()
        self.assertEqual(production.lot_producing_id.xx_weight, 50)
