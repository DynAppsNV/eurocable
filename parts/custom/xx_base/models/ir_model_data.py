from odoo import SUPERUSER_ID, _, api, models, tools
from odoo.exceptions import ValidationError


class IrModelData(models.Model):
    _inherit = "ir.model.data"

    @api.ondelete(at_uninstall=False)
    def _unlink_base_data(self):
        if (
            tools.config["test_enable"]
            or self.env.context.get("force_unlink_base_data", False)
            or self.env.user.id == SUPERUSER_ID
        ):
            return
        if self.filtered(lambda r: not r.model.startswith("ir.") and r.module.startswith("xx_")):
            raise ValidationError(_("Data defined in customization cannot be deleted!"))
