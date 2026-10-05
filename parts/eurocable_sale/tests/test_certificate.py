import base64
import io

from reportlab.pdfgen import canvas

from odoo.tests import TransactionCase, new_test_user, tagged
from odoo.tools.pdf import PdfFileReader


@tagged("post_install", "-at_install")
class TestCertificate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_eurocable = cls.env.company
        cls.company_cj = cls.env["res.company"].create({"name": "Constant Jacobs Test"})
        cls.user_cj = new_test_user(
            cls.env,
            login="cj_salesman",
            groups="sales_team.group_sale_salesman",
            company_id=cls.company_cj.id,
            company_ids=[(6, 0, cls.company_cj.ids)],
        )
        DocumentType = cls.env["document.type"]
        cls.doc_type_eurocable = DocumentType.create(
            {"name": "Eurocable Cert", "company_id": cls.company_eurocable.id}
        )
        cls.doc_type_cj = DocumentType.create({"name": "CJ Cert", "company_id": cls.company_cj.id})
        cls.doc_type_shared = DocumentType.create({"name": "Shared Cert"})
        cls.partner = cls.env["res.partner"].create({"name": "Certificate Customer"})
        cls.product = cls.env["product.product"].create({"name": "Test Cable"})

    def _create_confirmed_order(self, company):
        order = (
            self.env["sale.order"]
            .with_company(company)
            .create(
                {
                    "partner_id": self.partner.id,
                    "company_id": company.id,
                    "order_line": [(0, 0, {"product_id": self.product.id, "product_uom_qty": 1})],
                }
            )
        )
        order.action_confirm()
        return order

    def _blank_pdf(self):
        stream = io.BytesIO()
        pdf = canvas.Canvas(stream)
        pdf.showPage()
        pdf.save()
        return stream.getvalue()

    def test_document_type_visible_per_company(self):
        """A user only sees the certifications of their company and the shared ones."""
        visible = self.env["document.type"].with_user(self.user_cj).search([])
        self.assertIn(self.doc_type_cj, visible)
        self.assertIn(self.doc_type_shared, visible)
        self.assertNotIn(self.doc_type_eurocable, visible)

    def test_document_type_on_product_per_company(self):
        """The same product carries a different document type in each company."""
        template = self.product.product_tmpl_id
        template.with_company(self.company_eurocable).document_type_id = self.doc_type_eurocable
        template.with_company(self.company_cj).document_type_id = self.doc_type_cj

        order_eurocable = self._create_confirmed_order(self.company_eurocable)
        order_cj = self._create_confirmed_order(self.company_cj)
        self.assertEqual(order_eurocable.order_line.document_type, self.doc_type_eurocable)
        self.assertEqual(order_cj.order_line.document_type, self.doc_type_cj)

    def test_certificate_layout_per_company(self):
        """A company with certificate settings gets its own logo, stamp and signatory."""
        self.company_cj.write(
            {
                "xx_certificate_signatory": "Jane Jacobs",
                "xx_certificate_logo": self.env.company.logo,
                "xx_certificate_stamp": self.env.company.logo,
            }
        )
        report = self.env["ir.actions.report"]
        order_cj = self._create_confirmed_order(self.company_cj)
        html_cj = report._render_qweb_html(
            "eurocable_sale.report_certification", order_cj.order_line.ids
        )[0].decode()
        self.assertIn("Jane Jacobs", html_cj)
        self.assertNotIn("Paul Silles", html_cj)
        self.assertNotIn("eurocable_sale/static/img/logo.png", html_cj)

        order_eurocable = self._create_confirmed_order(self.company_eurocable)
        html_eurocable = report._render_qweb_html(
            "eurocable_sale.report_certification", order_eurocable.order_line.ids
        )[0].decode()
        self.assertIn("Paul Silles", html_eurocable)
        self.assertNotIn("Jane Jacobs", html_eurocable)
        self.assertIn("eurocable_sale/static/img/logo.png", html_eurocable)

    def test_print_certificate_download(self):
        """Without direct printing the user gets a download, otherwise nothing changes."""
        order = self._create_confirmed_order(self.company_cj)
        action = order.print_certificate()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertEqual(action["url"], f"/eurocable_sale/certificates/{order.id}")
        self.assertTrue(order.order_line.has_certificate)

        self.company_cj.printnode_enabled = True
        self.env.user.printnode_enabled = True
        order_dpc = self._create_confirmed_order(self.company_cj)
        self.assertIsNone(order_dpc.print_certificate())
        self.assertTrue(order_dpc.order_line.has_certificate)

    def test_certificate_bundle_contains_earlier_certificates(self):
        """The bundle holds every certificate of the order, also those of earlier prints."""
        order = self._create_confirmed_order(self.company_cj)
        order.print_certificate()
        order.order_line = [(0, 0, {"product_id": self.product.id, "product_uom_qty": 2})]
        order.print_certificate()
        attachments = order._get_certificate_attachments()
        self.assertEqual(len(attachments), 2)

        # Rendering returns html in test mode, so swap in real PDFs to check the merge
        attachments.write({"datas": base64.b64encode(self._blank_pdf())})
        bundle = order._get_certificate_bundle_pdf()
        self.assertEqual(len(PdfFileReader(io.BytesIO(bundle)).pages), 2)
