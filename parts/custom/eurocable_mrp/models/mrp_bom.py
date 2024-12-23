from odoo import api, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    # Calculate weight base on conditions
    def _compute_weight(self, record):
        weight_sum = 0.0
        for line in record.bom_line_ids.filtered(lambda s: s.product_id and s.product_qty > 0.0):
            # Divide weight by qty to get per unit weight
            weight_sum += line.product_id.weight * line.product_qty

        # If we are creating BOM for more than 1 qty of finish product
        if record.product_qty != 0:
            weight_sum = weight_sum / record.product_qty

        # Check for product variant
        if record.product_tmpl_id and record.product_id:
            record.product_id.weight = weight_sum
        else:
            record.product_tmpl_id.weight = weight_sum

    # Calculate total weight of finish product
    @api.model_create_multi
    def create(self, vals_list):
        boms = super().create(vals_list)
        for bom in boms:
            if bom.bom_line_ids:
                self._compute_weight(bom)
        return boms

    def write(self, vals):
        rec = super().write(vals)
        if "product_qty" or "product_tmpl_id" or "product_id" or "bom_line_ids" in vals:
            for bom in self:
                self._compute_weight(bom)
        return rec
