# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    document_type_id = fields.Many2one('document.type')
