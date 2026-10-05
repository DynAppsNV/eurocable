from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    document_type = fields.Many2one("document.type", compute="_compute_document_type")
    has_certificate = fields.Boolean(default=False)
    certificate_notes = fields.Text()
    sequence = fields.Integer(inverse="_inverse_sequence")
    xx_number = fields.Integer(string="Number")
    xx_hs_code = fields.Char(related="product_id.hs_code")

    @api.depends("product_id", "company_id")
    def _compute_document_type(self):
        # The document type depends on the company, so follow the order's company
        for line in self:
            line.document_type = line.product_id.with_company(line.company_id).document_type_id

    def _inverse_sequence(self):
        self.xx_number = 0
        for line in self.order_id.order_line.filtered(lambda li: not li.display_type):
            line.xx_number = (
                line.order_id.order_line.filtered(lambda li: not li.display_type)
                .sorted("sequence")
                .ids.index(line.id)
                + 1
            ) * 10

    def action_add_fixed_sale_phrase(self):
        return {
            "name": "Add Fixed Sale Phrase",
            "type": "ir.actions.act_window",
            "res_model": "xx.add.fixed.sale.phrase",
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
            "context": {
                "default_sale_order_ids": [self.env.context.get("order_id")],
            },
        }
