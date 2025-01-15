from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    weight_move = fields.Float(compute="_compute_total_weight", default=0.0)

    @api.depends("move_ids_without_package")
    def _compute_total_weight(self):
        for line in self:
            line.weight_move = sum(line.move_ids_without_package.mapped("total_weight"))

    def print_picking_label(self):
        self.ensure_one()
        multi_print_obj = self.env["stock.picking.label.layout"]
        multi_print_line_obj = self.env["stock.picking.label.layout.line"]

        view = self.env.ref("eurocable_stock.stock_picking_label_layout_form")

        wizard = multi_print_obj.create({"stock_picking_id": self.id})
        for move_line in self.move_line_ids_without_package:
            multi_print_line_obj.create(
                {
                    "wizard_id": wizard.id,
                    "stock_move_line_id": move_line.id,
                    "quantity": move_line.quantity,
                }
            )

        action = {
            "name": _("Print Picking Labels"),
            "type": "ir.actions.act_window",
            "res_model": "stock.picking.label.layout",
            "views": [(view.id, "form")],
            "target": "new",
            "res_id": wizard.id,
        }
        return action
