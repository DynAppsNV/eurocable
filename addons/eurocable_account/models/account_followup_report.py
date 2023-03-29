# -*- coding: utf-8 -*-
# Copyright 2023 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


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
                self.env['mail.mail'].sudo().create(mail_values).send()

            return True
        raise UserError(_('Could not send mail to partner %s because it does '
                          'not have any email address '
                          'defined', partner.display_name))
