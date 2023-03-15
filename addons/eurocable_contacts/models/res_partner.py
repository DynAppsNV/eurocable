# Copyright 2023
# Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_to = fields.Many2one('res.partner',
                                 help="partner used for payment reminder")

    def write(self, vals):
        if self.user_has_groups('eurocable_contacts.group_user_noedit'):
            raise UserError(_("You do not have access to edit the user details!"))
        return super().write(vals)

    def unlink(self):
        if self.user_has_groups('eurocable_contacts.group_user_noedit'):
            raise UserError(_("You do not have access to delete the user!"))
        return super().unlink()
