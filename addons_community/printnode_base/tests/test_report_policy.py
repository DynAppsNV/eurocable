# Copyright 2021 VentorTech OU
# See LICENSE file for full copyright and licensing details.
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools import mute_logger
from .common import TestPrintNodeCommon


@tagged('post_install', '-at_install', 'pn_report_policy')  # can be run by test-tag
class TestPrintNodeReport(TestPrintNodeCommon):

    def setUp(self):
        super(TestPrintNodeReport, self).setUp()
        self.company.printnode_recheck = False
        self.policy = self.env['printnode.report.policy'].create({
            'report_id': self.report.id,
        })

    @mute_logger('odoo.addons.printnode_base.models.printnode_printer')
    def test_printnode_module_disabled(self):
        self.company.printnode_enabled = False

        with self.assertRaises(UserError), self.cr.savepoint():
            self.printer.with_user(self.user.id).printnode_check_and_raise()

    @mute_logger('odoo.addons.printnode_base.models.printnode_printer')
    def test_printnode_recheck(self):
        self.company.printnode_enabled = True
        self.company.printnode_recheck = True

        with self.assertRaises(UserError), self.cr.savepoint(), \
                patch.object(type(self.account), 'recheck_printer', return_value=False):
            self.printer.with_user(self.user.id).printnode_check_and_raise()

    def test_printnode_no_recheck(self):
        self.company.printnode_enabled = True

        self.printer.with_user(self.user.id).printnode_check_and_raise()

    def test_printnode_policy_report_no_size_and_printer_no_size(self):
        self.company.printnode_enabled = True

        self.policy.report_paper_id = None
        self.printer.paper_ids = [(5, 0, 0)]

        self.printer.with_user(self.user.id).printnode_check_report(self.report)

    @mute_logger('odoo.addons.printnode_base.models.printnode_printer')
    def test_printnode_policy_report_no_size_and_printer_size(self):
        self.company.printnode_enabled = True

        self.policy.report_paper_id = None
        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a4').id])]

        with self.assertRaises(UserError), self.cr.savepoint():
            self.printer.with_user(self.user.id).printnode_check_report(self.report)

    @mute_logger('odoo.addons.printnode_base.models.printnode_printer')
    def test_printnode_policy_report_size_and_printer_no_size(self):
        self.company.printnode_enabled = True

        self.policy.report_paper_id = \
            self.env.ref('printnode_base.printnode_paper_a6')
        self.printer.paper_ids = [(5, 0, 0)]

        self.printer.with_user(self.user.id).printnode_check_report(self.report)

    @mute_logger('odoo.addons.printnode_base.models.printnode_printer')
    def test_printnode_policy_report_size_not_eq_printer_size(self):
        self.company.printnode_enabled = True

        self.policy.report_paper_id = \
            self.env.ref('printnode_base.printnode_paper_a6')
        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a4').id])]

        with self.assertRaises(UserError), self.cr.savepoint():
            self.printer.with_user(self.user.id).printnode_check_report(self.report)

    def test_printnode_policy_report_size_eq_printer_size(self):
        self.company.printnode_enabled = True

        self.policy.report_paper_id = \
            self.env.ref('printnode_base.printnode_paper_a6')
        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a6').id])]

        self.printer.with_user(self.user.id).printnode_check_report(self.report)

    @mute_logger('odoo.addons.printnode_base.models.printnode_printer')
    def test_printnode_policy_report_type_and_printer_no_type(self):
        self.company.printnode_enabled = True

        self.policy.report_type = 'qweb-pdf'
        self.printer.format_ids = [(5, 0, 0)]

        self.printer.with_user(self.user.id).printnode_check_report(self.report)

    @mute_logger('odoo.addons.printnode_base.models.printnode_printer')
    def test_printnode_policy_report_type_not_eq_printer_type(self):
        self.company.printnode_enabled = True

        self.policy.report_type = 'qweb-pdf'
        self.printer.format_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_content_type_raw').id])]

        with self.assertRaises(UserError), self.cr.savepoint():
            self.printer.with_user(self.user.id).printnode_check_report(self.report)

    def test_printnode_policy_report_type_eq_printer_type(self):
        self.company.printnode_enabled = True

        self.policy.report_type = 'qweb-pdf'
        self.printer.format_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_content_type_pdf').id])]

        self.printer.with_context(user=self.user).printnode_check_report(self.report)

    @mute_logger('odoo.addons.printnode_base.models.printnode_printer')
    def test_printnode_policy_attachment_wrong_type(self):
        self.company.printnode_enabled = True

        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a4').id])]
        self.printer.format_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_content_type_raw').id])]

        with self.assertRaises(UserError), self.cr.savepoint():
            self.printer.with_user(self.user.id).printnode_check_and_raise({
                'title': 'Label',
                'type': 'qweb-pdf',
                'size': self.env.ref('printnode_base.printnode_paper_a4'),
            })

    @mute_logger('odoo.addons.printnode_base.models.printnode_printer')
    def test_printnode_policy_attachment_wrong_size(self):
        self.company.printnode_enabled = True

        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a6').id])]
        self.printer.format_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_content_type_pdf').id])]

        with self.assertRaises(UserError), self.cr.savepoint():
            self.printer.with_user(self.user.id).printnode_check_and_raise({
                'title': 'Label',
                'type': 'qweb-pdf',
                'size': self.env.ref('printnode_base.printnode_paper_a4'),
            })

    @mute_logger('odoo.addons.printnode_base.models.printnode_printer')
    def test_printnode_policy_attachment_empty_params(self):
        self.company.printnode_enabled = True

        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a4').id])]
        self.printer.format_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_content_type_pdf').id])]

        with self.assertRaises(UserError):
            self.printer.with_user(self.user.id).printnode_check_and_raise({
                'title': 'Label',
            })

    def test_printnode_policy_attachment_valid_params(self):
        self.company.printnode_enabled = True

        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a4').id])]
        self.printer.format_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_content_type_pdf').id])]

        self.printer.with_user(self.user.id).printnode_check_and_raise({
            'title': 'Label',
            'type': 'qweb-pdf',
            'size': self.env.ref('printnode_base.printnode_paper_a4'),
        })

    def test_compute_print_rules(self):
        """Test for the correct compute print rules"""

        self.policy.report_id = self.so_report.id

        self.policy.exclude_from_auto_printing = True
        self.assertFalse(self.policy.error)
        self.assertTrue('fa-circle-o' in self.policy.notes)

        self.policy.exclude_from_auto_printing = False
        self.assertTrue(self.policy.error)
        self.assertTrue('fa-exclamation-circle' in self.policy.notes)

        self.env.company.printnode_enabled = True
        self.policy._compute_print_rules()
        self.assertFalse(self.policy.error)
        self.assertTrue('fa-circle-o' in self.policy.notes)
