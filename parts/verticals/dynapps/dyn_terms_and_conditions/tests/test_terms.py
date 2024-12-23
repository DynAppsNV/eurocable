import base64

from odoo.exceptions import ValidationError
from odoo.tests import common, patch
from odoo.tools.misc import file_open


class TestTerms(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, force_report_rendering=True))
        cls.term_obj = cls.env["term.term"]
        cls.rule_obj = cls.env["term.rule"]
        cls.term_begin = cls.term_obj.create(
            {
                "name": "Test Begin Term",
                "mode": "begin",
                "pdf": base64.b64encode(cls._get_pdf()),
            }
        )
        cls.term_duplex = cls.term_obj.create(
            {
                "name": "Test Duplex Term",
                "mode": "duplex",
                "pdf": base64.b64encode(cls._get_pdf()),
            }
        )
        cls.term_end = cls.term_obj.create(
            {
                "name": "Test End Term",
                "mode": "end",
                "pdf": base64.b64encode(cls._get_pdf()),
            }
        )
        cls.term_txttoimg = cls.term_obj.create(
            {
                "name": "Test Text Term",
                "text": "TEST",
                "mode": "txttoimg",
                "pdf": base64.b64encode(cls._get_pdf()),
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.report = cls.env.ref("base.ir_module_reference_print")
        cls.module = cls.env.ref("base.module_dyn_terms_and_conditions")
        cls.company = cls.env.ref("base.main_company")
        cls.other_company = cls.env["res.company"].create({"name": "Other Company"})

    @staticmethod
    def _get_pdf():
        return file_open("base/tests/minimal.pdf", "rb").read()

    @patch("odoo.addons.dyn_terms_and_conditions.models.term_rule.TermRule._add_end_terms")
    @patch("odoo.addons.dyn_terms_and_conditions.models.term_rule.TermRule._add_txttoimg_terms")
    @patch("odoo.addons.dyn_terms_and_conditions.models.term_rule.TermRule._add_duplex_terms")
    @patch("odoo.addons.dyn_terms_and_conditions.models.term_rule.TermRule._add_begin_terms")
    @patch("odoo.addons.base.models.ir_actions_report.IrActionsReport._run_wkhtmltopdf")
    def test_01_functions_called(
        self,
        patched_run_wkhtmltopdf,
        patched_add_begin_terms,
        patched_add_duplex_terms,
        patched_add_txttoimg_terms,
        patched_add_end_terms,
    ):
        patched_run_wkhtmltopdf.return_value = self._get_pdf()
        self.env["ir.actions.report"]._render_qweb_pdf(
            report_ref=self.report.get_external_id().get(self.report.id), res_ids=[self.module.id]
        )
        patched_run_wkhtmltopdf.assert_called()
        patched_add_begin_terms.assert_not_called()
        patched_add_duplex_terms.assert_not_called()
        patched_add_txttoimg_terms.assert_not_called()
        patched_add_end_terms.assert_not_called()

    @patch("odoo.addons.base.models.ir_actions_report.IrActionsReport._run_wkhtmltopdf")
    def test_02_begin_terms_condition(self, patched_run_wkhtmltopdf):
        patched_run_wkhtmltopdf.return_value = self._get_pdf()
        with self.assertRaisesRegex(
            ValidationError, "Incorrect condition specified: .*name 'obj' is not defined"
        ), self.cr.savepoint():
            self.rule_obj.create(
                {
                    "term_id": self.term_begin.id,
                    "company_id": self.company.id,
                    "report_id": self.report.id,
                    "condition": f"obj.name == {self.module.name}",
                }
            )
        self.rule_obj.create(
            {
                "term_id": self.term_begin.id,
                "company_id": self.company.id,
                "report_id": self.report.id,
                "condition": f"object.name == '{self.module.name}'",
            }
        )
        self.env["ir.actions.report"]._render_qweb_pdf(
            report_ref=self.report.get_external_id().get(self.report.id), res_ids=[self.module.id]
        )

        with patch(
            "odoo.addons.dyn_terms_and_conditions.models.term_rule.TermRule._add_begin_terms"
        ) as patched_add_begin_terms:
            self.env["ir.actions.report"].with_company(self.other_company)._render_qweb_pdf(
                report_ref=self.report.get_external_id().get(self.report.id),
                res_ids=[self.module.id],
            )
            patched_add_begin_terms.assert_not_called()

    @patch("odoo.addons.base.models.ir_actions_report.IrActionsReport._run_wkhtmltopdf")
    def test_03_duplex_terms_condition(self, patched_run_wkhtmltopdf):
        patched_run_wkhtmltopdf.return_value = self._get_pdf()
        self.rule_obj.create(
            {
                "term_id": self.term_duplex.id,
                "company_id": self.company.id,
                "report_id": self.report.id,
                "condition": f"object.name == '{self.module.name}'",
            }
        )
        self.env["ir.actions.report"]._render_qweb_pdf(
            report_ref=self.report.get_external_id().get(self.report.id), res_ids=[self.module.id]
        )

    @patch("odoo.addons.base.models.ir_actions_report.IrActionsReport._run_wkhtmltopdf")
    def test_04_txttoimg_terms_condition(self, patched_run_wkhtmltopdf):
        patched_run_wkhtmltopdf.return_value = self._get_pdf()
        self.rule_obj.create(
            {
                "term_id": self.term_txttoimg.id,
                "company_id": self.company.id,
                "report_id": self.report.id,
                "condition": f"object.name == '{self.module.name}'",
            }
        )
        self.env["ir.actions.report"]._render_qweb_pdf(
            report_ref=self.report.get_external_id().get(self.report.id), res_ids=[self.module.id]
        )

    @patch("odoo.addons.base.models.ir_actions_report.IrActionsReport._run_wkhtmltopdf")
    def test_05_end_terms_condition(self, patched_run_wkhtmltopdf):
        patched_run_wkhtmltopdf.return_value = self._get_pdf()
        self.rule_obj.create(
            {
                "term_id": self.term_end.id,
                "company_id": self.company.id,
                "report_id": self.report.id,
                "condition": f"object.name == '{self.module.name}'",
            }
        )
        self.env["ir.actions.report"]._render_qweb_pdf(
            report_ref=self.report.get_external_id().get(self.report.id), res_ids=[self.module.id]
        )
