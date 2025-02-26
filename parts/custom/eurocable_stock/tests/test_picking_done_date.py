from datetime import datetime, timedelta

from odoo import Command
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPickingDoneDate(TransactionCase):
    def setUp(self):
        super().setUpClass()
        self.scheduled_date = datetime.now() + timedelta(days=2)
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.product = self.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )
        self.picking = self.env["stock.picking"].create(
            {
                "scheduled_date": self.scheduled_date,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "move_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                        }
                    )
                ],
            }
        )

    def test_picking_done_date(self):
        self.picking.button_validate()
        self.assertEqual(self.picking.date_done, self.scheduled_date)
