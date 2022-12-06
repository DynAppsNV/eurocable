# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for move in self:
            move.to_check = True
        res = super(AccountMove, self).action_post()
        return res
