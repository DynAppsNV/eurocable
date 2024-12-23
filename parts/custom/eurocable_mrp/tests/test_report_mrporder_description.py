from odoo import Command
from odoo.tests import Form
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReportMrpOrderDescription(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.ref("stock.route_warehouse0_mto").active = True  # Unarchive MTO route
        cls.product_manu = cls.browse_ref(cls, "product.product_product_8")
        cls.product_manu.write(
            {
                "route_ids": (
                    cls.browse_ref(cls, "stock.route_warehouse0_mto")
                    | cls.browse_ref(cls, "mrp.route_warehouse0_manufacture")
                ).ids,
                "bom_ids": [
                    Command.create(
                        {
                            "product_tmpl_id": cls.product_manu.product_tmpl_id.id,
                            "product_id": cls.product_manu.id,
                            "product_qty": 1,
                            "type": "normal",
                            "bom_line_ids": [
                                Command.create(
                                    {
                                        "product_id": cls.browse_ref(
                                            cls, "product.product_delivery_01"
                                        ).id,
                                        "product_qty": 5,
                                    }
                                ),
                                Command.create(
                                    {
                                        "product_id": cls.browse_ref(
                                            cls, "product.product_delivery_02"
                                        ).id,
                                        "product_qty": 10,
                                    }
                                ),
                            ],
                        }
                    )
                ],
            }
        )
        cls.custom_text = "Test Line 1\nTest Line 2\nTest Line 3"

    def test_01_report_mrporder_description(self):
        """Test the transition of the description from SO to MO (with intact formatting)."""
        with Form(self.env["sale.order"]) as form:
            form.partner_id = self.browse_ref("base.res_partner_2")
            with form.order_line.new() as line:
                line.product_id = self.product_manu
                line.name += self.custom_text
        so = form.save()
        so.action_confirm()
        self.assertEqual(so.mrp_production_count, 1)
        mo = self.env["mrp.production"].browse(so.action_view_mrp_production()["res_id"])
        self.assertTrue(mo.xx_product_description_variants.endswith(self.custom_text))
