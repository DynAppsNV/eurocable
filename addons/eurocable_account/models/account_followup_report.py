# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, api, fields
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang, format_date, get_lang


class AccountFollowupReport(models.AbstractModel):
    _inherit = "account.followup.report"

    @api.model
    def send_email(self, options):
        """
        Send by mail the followup to the customer
        """
        partner = self.env['res.partner'].browse(options.get('partner_id'))
        non_blocked_amls = partner.unreconciled_aml_ids.\
            filtered(lambda aml: not aml.blocked)
        if not non_blocked_amls:
            return True
        non_printed_invoices = partner.unpaid_invoices.\
            filtered(lambda inv: not inv.message_main_attachment_id)
        if non_printed_invoices and partner.followup_level.join_invoices:
            raise UserError(
                _('You are trying to send a followup report to a partner for '
                  'which you didn\'t print all the invoices ({})').format(
                    " ".join(non_printed_invoices.mapped('name'))))
        invoice_partner = self.env['res.partner'].\
            browse(partner.address_get(['invoice'])['invoice'])
        email = invoice_partner.email
        if email and email.strip():
            self = self.with_context(lang=partner.lang or self.env.user.lang)
            template = self.env.\
                ref('eurocable_contacts.email_template_payment_reminder')
            if template:
                mail_values = {'body_html': template.body_html,
                               'subject': self._get_report_manager(options).
                               email_subject,
                               'email_to': partner.partner_to.email or email}
                template.send_mail(partner.id, force_send=True,
                                   email_values=mail_values)
            return True
        raise UserError(_('Could not send mail to partner %s because it does '
                          'not have any email address '
                          'defined', partner.display_name))

    # Override for formatting purpose
    def _get_columns_name(self, options):
        """
        Override
        Return the name of the columns of the follow-ups report
        """
        headers = [{},
                   {'name': _('Date'), 'class': 'date',
                    'style': 'text-align:center; '
                             'white-space:nowrap; padding:5px;'},
                   {'name': _('Due Date'), 'class': 'date',
                    'style': 'text-align:center; padding:5px;'},
                   {'name': _('Source Document'),
                    'style': 'text-align:center;'},
                   {'name': _('Communication'),
                    'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Expected Date'), 'class': 'date',
                    'style': 'white-space:nowrap;'},
                   {'name': _('Excluded'), 'class': 'date',
                    'style': 'white-space:nowrap;'},
                   {'name': _('Total Due'), 'class': 'number o_price_total',
                    'style': 'text-align:center; white-space:nowrap;'}
                   ]
        if self.env.context.get('print_mode'):
            # Remove the 'Source Document', 'Expected Date' and
            # 'Excluded' columns
            indices_to_remove = [3, 5, 6]
            headers = [headers[i] for i in range(len(headers))
                       if i not in indices_to_remove]
        return headers

    # Override method for remove 'Source Document' column
    def _get_lines(self, options, line_id=None):
        """
        Override
        Compute and return the lines of the columns of the follow-ups report.
        """
        # Get date format for the lang
        partner = options.get('partner_id') and self.env['res.partner'].\
            browse(options['partner_id']) or False
        if not partner:
            return []

        lang_code = partner.lang if self._context.get('print_mode') else \
            self.env.user.lang or get_lang(self.env).code
        lines = []
        res = {}
        today = fields.Date.today()
        line_num = 0
        for l in partner.unreconciled_aml_ids.sorted().\
                filtered(lambda aml: not
        aml.currency_id.is_zero(aml.amount_residual_currency)):
            if l.company_id == self.env.company:
                if self.env.context.get('print_mode') and l.blocked:
                    continue
                currency = l.currency_id or l.company_id.currency_id
                if currency not in res:
                    res[currency] = []
                res[currency].append(l)
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            for aml in aml_recs:
                amount = aml.amount_residual_currency if aml.currency_id else\
                    aml.amount_residual
                date_due = format_date(self.env, aml.date_maturity or
                                       aml.move_id.invoice_date or aml.date,
                                       lang_code=lang_code)
                total += not aml.blocked and amount or 0
                is_overdue = today > aml.date_maturity if aml.date_maturity\
                    else today > aml.date
                is_payment = aml.payment_id
                if is_overdue or is_payment:
                    total_issued += not aml.blocked and amount or 0
                if is_overdue:
                    date_due = {'name': date_due, 'class': 'color-red date',
                                'style': 'white-space:nowrap; '
                                         'text-align:center;color: red;'}
                if is_payment:
                    date_due = ''
                move_line_name = self._format_aml_name(aml.name,
                                                       aml.move_id.ref)
                if self.env.context.get('print_mode'):
                    move_line_name = {'name': move_line_name,
                                      'style': 'text-align:right; '
                                               'white-space:normal;'}
                amount = formatLang(self.env, amount, currency_obj=currency)
                line_num += 1
                expected_pay_date = format_date(self.env,
                                                aml.expected_pay_date,
                                                lang_code=lang_code) if \
                    aml.expected_pay_date else ''
                invoice_origin = aml.move_id.invoice_origin or ''
                if len(invoice_origin) > 43:
                    invoice_origin = invoice_origin[:40] + '...'
                columns = [
                    format_date(self.env, aml.move_id.invoice_date or
                                aml.date, lang_code=lang_code),
                    date_due,
                    invoice_origin,
                    move_line_name,
                    (expected_pay_date and expected_pay_date + ' ') +
                    (aml.internal_note or ''),
                    {'name': '', 'blocked': aml.blocked},
                    amount,
                ]
                if self.env.context.get('print_mode'):
                    indices_to_remove = [2, 4, 5]
                    columns = [columns[i] for i in range(len(columns))
                               if i not in indices_to_remove]
                    # columns = columns[:4] + columns[6:]
                lines.append({
                    'id': aml.id,
                    'account_move': aml.move_id,
                    'name': aml.move_id.name,
                    'caret_options': 'followup',
                    'move_id': aml.move_id.id,
                    'type': is_payment and 'payment' or 'unreconciled_aml',
                    'unfoldable': False,
                    'columns': [type(v) == dict and v or {'name': v}
                                for v in columns],
                })
            total_due = formatLang(self.env, total, currency_obj=currency)
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': 'total',
                'style': 'border-top-style: double',
                'unfoldable': False,
                'level': 3,
                'columns': [{'name': v} for v in [''] *
                            (2 if self.env.context.get('print_mode') else 5)
                            + [total >= 0 and _('Total Due') or '',
                               total_due]],
            })
            if total_issued > 0:
                total_issued = formatLang(self.env, total_issued,
                                          currency_obj=currency)
                line_num += 1
                lines.append({
                    'id': line_num,
                    'name': '',
                    'class': 'total',
                    'unfoldable': False,
                    'level': 3,
                    'columns': [{'name': v} for v in [''] *
                                (2 if self.env.context.get('print_mode')
                                 else 5) + [_('Total Overdue'),
                                            total_issued]],
                })
            # Add an empty line after the total to make a space between two
            # currencies
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': '',
                'style': 'border-bottom-style: none',
                'unfoldable': False,
                'level': 0,
                'columns': [{} for col in columns],
            })
        # Remove the last empty line
        if lines:
            lines.pop()
        return lines
