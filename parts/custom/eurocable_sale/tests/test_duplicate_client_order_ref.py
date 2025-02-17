from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDuplicateClientOrderRef(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        (
            cls.sale_order,
            cls.sale_order_duplicate,
            cls.sale_order_another,
            cls.sale_order_empty,
        ) = cls.env["sale.order"].create([{"partner_id": cls.env.ref("base.res_partner_1").id}] * 4)
        (cls.sale_order | cls.sale_order_duplicate).write({"client_order_ref": "Same Reference"})
        cls.sale_order_another.client_order_ref = "Another Reference"

    def test_duplicate_client_order_ref(self):
        """Test whether duplicate customer references are detected correctly."""
        self.assertEqual(self.sale_order.xx_same_client_order_ref_id, self.sale_order_duplicate)
        self.assertEqual(self.sale_order_duplicate.xx_same_client_order_ref_id, self.sale_order)
        self.assertFalse(self.sale_order_another.xx_same_client_order_ref_id)
        self.assertFalse(self.sale_order_empty.xx_same_client_order_ref_id)
