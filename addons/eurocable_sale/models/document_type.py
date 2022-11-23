# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class DocumentType(models.Model):
    _name = "document.type"

    name = fields.Char(required=True)
    text = fields.Html(translate=True)
