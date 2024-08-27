from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestFixedPhrases(common.TransactionCase):
    def setUp(self):
        super().setUp()

    def test_01_create_and_add_fixed_sale_phrase(self):
        fixed_sale_phrase_1 = self.env["xx.fixed.sale.phrase"].create(
            {
                "name": "Test Phrase",
                "phrase": "This is a test phrase",
            }
        )
        fixed_sale_phrase_2 = self.env["xx.fixed.sale.phrase"].create(
            {
                "name": "Another Test Phrase",
                "phrase": "This is another test phrase",
            }
        )

        # Create a sale order
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
            }
        )

        # create an add fixed sale phrase wizard
        add_fixed_sale_phrase_wizard = self.env["xx.add.fixed.sale.phrase"].create(
            {
                "sale_order_ids": [(6, 0, sale_order.ids)],
            }
        )

        # Add the fixed sale phrase to the sale order
        add_fixed_sale_phrase_wizard.fixed_sale_phrase_ids = [
            (6, 0, [fixed_sale_phrase_1.id, fixed_sale_phrase_2.id])
        ]
        add_fixed_sale_phrase_wizard.add_fixed_sale_phrase()

        # Check if the fixed sale phrases are added to the sale order
        for sol in sale_order.order_line.filtered(lambda sl: sl.display_type == "line_note"):
            self.assertIn(sol.name, [fixed_sale_phrase_1.phrase, fixed_sale_phrase_2.phrase])
