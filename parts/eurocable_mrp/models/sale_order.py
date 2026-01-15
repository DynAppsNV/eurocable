from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    mrp_production_count = fields.Integer(store=True)
    mrp_production_ids = fields.Many2many(store=True)
    xx_procurement_group_ids = fields.One2many(
        comodel_name="procurement.group",
        inverse_name="sale_id",
        string="Procurement Groups",
    )

    @api.depends(
        "xx_procurement_group_ids.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids",
        "xx_procurement_group_ids.mrp_production_ids",
    )
    def _compute_mrp_production_ids(self):
        for order in self:
            mrp_productions = (
                order.xx_procurement_group_ids.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids
                | order.xx_procurement_group_ids.mrp_production_ids
            )
            order.mrp_production_count = len(mrp_productions)
            order.mrp_production_ids = mrp_productions.ids
