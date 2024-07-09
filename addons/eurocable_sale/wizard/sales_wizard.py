from odoo import api, fields, models


class SalesWizard(models.TransientModel):
    _name = "sales.wizard"
    _description = "sales wizard"

    sales_id = fields.Many2one("sale.order")
    message = fields.Text(string="The VAT field of partner is empty", readonly=True, store=True)

    @api.model
    def default_get(self, fields):
        vals = super().default_get(fields)
        active_id = self.env.context.get("active_id")
        sale = self.env["sale.order"].browse(active_id)
        vals["sales_id"] = sale.id
        return vals

    def confirm_sale_order(self):
        return self.sales_id.action_confirm()
