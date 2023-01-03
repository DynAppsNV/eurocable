# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move.line"

    intrastat_id = fields.Many2one('account.intrastat.code',
                                   store=True, string="Commodity code")
    weight = fields.Float(store=True, default=0.0, )
    co_commd = fields.Char(related='product_id.intrastat_id.code', store=True)
    uom_id = fields.Many2one('uom.uom')
    uom_category_id = fields.Many2one('uom.category')
    intrastat_product_origin_country_name = fields.Char(
        related='product_id.intrastat_origin_country_id.name')
    factor = fields.Float()
    region_code = fields.Integer(default=1)

    @api.onchange('product_id')
    def compute_intrastat_code(self):
        intrastat_transaction_id = self.env['account.intrastat.code'].search([('code', '=', 11)]).id
        for rec in self:
            rec.intrastat_transaction_id = intrastat_transaction_id
            if rec.product_id:
                rec.intrastat_id = rec.product_id.intrastat_id
                rec.weight = rec.product_id.weight
                rec.uom_id = rec.product_id.uom_id
                rec.uom_category_id = rec.uom_id.category_id
                rec.factor = rec.uom_id.factor

