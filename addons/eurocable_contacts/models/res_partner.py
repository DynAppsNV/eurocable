# -*- encoding: utf-8 -*-
# Copyright 2023      Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_to = fields.Many2one('res.partner')
