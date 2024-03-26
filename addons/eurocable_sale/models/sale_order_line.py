from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    document_type = fields.Many2one(related="product_id.document_type_id")
    has_certificate = fields.Boolean(default=False)
    certificate_notes = fields.Text()
    weight = fields.Float(default=0.0)
    weight_total = fields.Float(default=0.0, compute="_compute_total_weight")

    @api.onchange("product_id")
    def _compute_weight(self):
        if self.product_id:
            self.weight = self.product_id.weight

    @api.depends("product_template_id", "product_id", "product_uom_qty", "weight")
    def _compute_total_weight(self):
        for rec in self:
            rec.weight_total = 0.0
            if rec.weight:
                rec.weight_total = rec.weight * rec.product_uom_qty

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res.update({"weight": self.weight})
        return res
