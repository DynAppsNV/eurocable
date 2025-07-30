from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    xx_weight = fields.Float(string="Weight per Unit", compute="_compute_total_weight", store=True)
    xx_product_description_variants = fields.Text("Custom Description")
    xx_customer_ids = fields.Many2many(
        comodel_name="res.partner", compute="_compute_customers", store=True
    )
    xx_sale_line_id = fields.Many2one(string="Sale Line", comodel_name="sale.order.line")

    @api.depends("move_raw_ids.xx_weight", "origin")
    def _compute_total_weight(self):
        for rec in self:
            rec.xx_weight = 0
            for move in rec.move_raw_ids:
                rec.xx_weight += move.xx_weight
            rec.xx_weight /= rec.product_qty or 1.0

            sale_order = self.env["sale.order"].search([("name", "=", rec.origin)])
            for line in sale_order.order_line:
                line._compute_weight()

    @api.depends(
        "procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id.partner_id"
    )
    def _compute_customers(self):
        for rec in self:
            partners = rec.mapped(
                "procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id.partner_id"
            )
            rec.xx_customer_ids = partners.browse(
                [p.id if p.name else p.parent_id.id for p in partners]
            )
