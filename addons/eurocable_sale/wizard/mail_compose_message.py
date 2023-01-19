# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_send_mail(self):
        default_attachment_ids = self._context.get('default_attachment_ids')
        if default_attachment_ids:
            for wizard in self:
                attachment_ids = default_attachment_ids + wizard.attachment_ids.ids
                wizard.attachment_ids = [(6, 0, attachment_ids)]
        return super(MailComposer, self).action_send_mail()
