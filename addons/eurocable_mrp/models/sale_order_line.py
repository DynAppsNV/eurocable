from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    weight = fields.Float(compute="_compute_weight", store=True, readonly=False)
    weight_total = fields.Float(compute="_compute_total_weight", store=True)

    def _compute_weight(self):
        for rec in self:
            rec.weight = rec.order_id.mrp_production_ids.filtered(
                lambda x: x.product_id == rec.product_id and x.procurement_group_id == rec.procurement_group_id
            ).xx_weight

    @api.depends("product_uom_qty", "weight")
    def _compute_total_weight(self):
        for rec in self:
            rec.weight_total = rec.weight * rec.product_uom_qty if rec.weight else 0.0

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res.update({"weight": self.weight})
        return res
