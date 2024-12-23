from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SystemOption(models.AbstractModel):
    _name = "xx.system.option"
    _description = "System Option"

    xx_system_option = fields.Boolean("System Option ?", default=False, readonly=True)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_system_option(self):
        for rec in self:
            if rec.xx_system_option:
                raise ValidationError(_("A system option cannot be deleted!"))
