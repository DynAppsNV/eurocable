from odoo import _, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    send_so_to_inv = fields.Boolean("Send SO info with invoice", default=False, copy=False)
    partner_to = fields.Many2one("res.partner", help="partner used for payment reminder")

    def write(self, vals):
        if (
            self.user_has_groups("eurocable_contacts.group_user_noedit")
            and not self.type == "delivery"
        ):
            raise UserError(_("You do not have access to edit the user details!"))
        return super().write(vals)

    def unlink(self):
        if self.user_has_groups("eurocable_contacts.group_user_noedit"):
            raise UserError(_("You do not have access to delete the user!"))
        return super().unlink()
