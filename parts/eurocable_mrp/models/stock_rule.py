from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(
        self,
        product_id,
        product_qty,
        product_uom,
        location_dest_id,
        name,
        origin,
        company_id,
        values,
        bom,
    ):
        """Copy field with conservation of formatting. Needed for the MO report."""
        mo_values = super()._prepare_mo_vals(
            product_id,
            product_qty,
            product_uom,
            location_dest_id,
            name,
            origin,
            company_id,
            values,
            bom,
        )
        mo_values["xx_product_description_variants"] = values.get(
            "product_description_variants"
        ).strip()
        mo_values["xx_sale_line_id"] = values.get("sale_line_id")
        return mo_values
