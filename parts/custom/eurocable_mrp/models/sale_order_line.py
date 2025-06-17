from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    xx_debug_weight = fields.Float(compute="_compute_debug_weight", store=True, tracking=True)

    @api.depends("order_line.weight")
    def _compute_debug_weight(self):
        for order in self:
            order.xx_debug_weight = 0
            if order.order_line:
                order.write({"xx_debug_weight": order.order_line[0].weight})

    def write(self, values):
        for order in self:
            if "xx_debug_weight" in values and order.xx_debug_weight:
                order.message_post(body=f"Debug: Weight changed - {values['xx_debug_weight']}")
        super().write(values)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    weight = fields.Float(compute="_compute_weight", store=True, readonly=False)
    weight_total = fields.Float(compute="_compute_total_weight", store=True)

    @api.depends(
        "product_id.weight",
        "product_id.bom_ids",
        "order_id.mrp_production_ids",
        "order_id.mrp_production_ids.product_id",
        "order_id.mrp_production_ids.xx_sale_line_id",
    )
    def _compute_weight(self):
        for rec in self:
            weight = 0
            if rec.product_id:
                production = rec.order_id.mrp_production_ids.filtered(
                    lambda x: x.xx_sale_line_id.id == rec.id  # noqa: B023
                )
                if production:
                    weight = production.xx_weight
                else:
                    weight = rec.product_id.weight
            rec.weight = weight

    @api.depends("product_uom_qty", "weight")
    def _compute_total_weight(self):
        for rec in self:
            rec.weight_total = rec.weight * rec.product_uom_qty if rec.weight else 0.0

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res.update({"weight": self.weight})
        return res
