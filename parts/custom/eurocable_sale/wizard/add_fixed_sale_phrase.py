from odoo import fields, models


class AddFixedSalePhrase(models.TransientModel):
    _name = "xx.add.fixed.sale.phrase"
    _description = "Wizard to add a Fixed Sale Phrase to the Sale Order"

    sale_order_ids = fields.Many2many(comodel_name="sale.order")
    fixed_sale_phrase_ids = fields.Many2many(comodel_name="xx.fixed.sale.phrase")

    def add_fixed_sale_phrase(self):
        if self.sale_order_ids and self.fixed_sale_phrase_ids:
            for so in self.sale_order_ids:
                for phrase in self.fixed_sale_phrase_ids:
                    self.env["sale.order.line"].create(
                        {"order_id": so.id, "display_type": "line_note", "name": phrase.phrase}
                    )
