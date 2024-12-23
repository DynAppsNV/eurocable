from odoo import models


class AuditRule(models.Model):
    _inherit = "audit.rule"

    def log(self, method, old_values=None, new_values=None):
        self.ensure_one()
        model = self.sudo().model_id.model
        if old_values or new_values:
            data = self._format_data_to_log(old_values, new_values)
            auditlog_obj = self.env["audit.log"].sudo()
            for res_id in data:
                auditlog_obj.create(
                    {
                        "user_id": self._uid,
                        "model_id": self.sudo().model_id.id,
                        "res_id": res_id,
                        "method": method,
                        "data": repr(data[res_id]),
                    }
                )
                if model == "product.template" or "product.product":
                    model_id = self.env[model].browse(res_id)
                    model_id.message_post(
                        body=(
                            "<b>"
                            + "Les anciennes valeurs :"
                            + "</b>"
                            + repr(data[res_id]["old"])
                            + "<br/> <b>"
                            + "Les nouvelles valeurs:"
                            + "</b>"
                            + repr(data[res_id]["new"])
                        )
                    )
        return True
