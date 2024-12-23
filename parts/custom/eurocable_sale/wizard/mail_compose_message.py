from odoo import models


class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    def action_send_mail(self):
        default_attachment_ids = self._context.get("default_attachment_ids")
        if default_attachment_ids:
            for wizard in self:
                attachment_ids = default_attachment_ids + wizard.attachment_ids.ids
                wizard.attachment_ids = [(6, 0, attachment_ids)]
        return super().action_send_mail()
