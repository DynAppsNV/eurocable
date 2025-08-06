import logging

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    term_rule_ids = fields.One2many(
        comodel_name="term.rule",
        inverse_name="report_id",
        help="List of possible terms to be added.",
    )

    @api.model
    def get_valid_term_rules(self, report_ref):
        report = self._get_report(report_ref)
        rule_obj = self.env["term.rule"]
        rule_ids = rule_obj.search([("report_name", "=", report.report_name)])
        valid_rules = self.env["term.rule"]
        for rule in rule_ids:
            _logger.debug("Checking rule %s for report %s", rule.term_id.name, report.report_name)

            if rule.company_id:
                if rule.company_id != self.env.company:
                    _logger.debug("Company id's did not match !")
                    continue
                else:
                    _logger.debug("Company id's matched !")

            # User has specified a condition, check it and return res when not met
            if safe_eval(rule.condition, rule_obj._get_terms_env(report.model)):
                valid_rules |= rule
        return valid_rules

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        if not self.env.context.get("res_ids"):
            return super(
                IrActionsReport, self.env["ir.actions.report"].with_context(res_ids=res_ids)
            )._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
        return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

    @api.model
    def _run_wkhtmltopdf(
        self,
        bodies,
        report_ref=False,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        result = super()._run_wkhtmltopdf(
            bodies,
            report_ref=report_ref,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
        valid_rules = self.get_valid_term_rules(report_ref)
        if not valid_rules:
            return result
        return valid_rules.add_terms(result)
