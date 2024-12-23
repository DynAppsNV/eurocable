from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockPickingLabelLayout(models.TransientModel):
    _name = "stock.picking.label.layout"
    _description = "Choose the sheet layout to print the labels"

    stock_picking_id = fields.Many2one("stock.picking", string="Stock picking")
    print_format = fields.Selection(
        [("green_card_zpl", "Green card ZPL Labels")], default="green_card_zpl"
    )
    printer_id = fields.Many2one(
        comodel_name="printnode.printer",
        default=lambda self: self._default_printer_id(),
    )
    custom_quantity = fields.Integer("Quantity", default=1)
    printer_bin = fields.Many2one(
        "printnode.printer.bin",
        required=False,
        domain='[("printer_id", "=", printer_id)]',
    )
    label_line_ids = fields.One2many(
        comodel_name="stock.picking.label.layout.line",
        inverse_name="wizard_id",
        string="Products",
    )
    status = fields.Char(
        related="printer_id.status",
    )
    is_dpc_enabled = fields.Boolean(
        default=lambda self: self._is_dpc_enabled(),
    )

    def _default_printer_id(self):
        """
        Returns only default printer from _get_default_printer()
        """
        printer, _ = self._get_default_printer()
        return printer

    def _get_default_printer(self):
        """
        Returns default printer for the user if DPC module enabled, otherwise - returns None
        """
        if self._is_dpc_enabled():
            # User rules
            try:
                report_xml_id, _ = self._prepare_report_data()
                report_id = self.env.ref(report_xml_id)
            except UserError:
                # Skip custom interface errors
                report_id = self.env["ir.actions.report"]

            user_rules = self.env["printnode.rule"].search(
                [
                    ("user_id", "=", self.env.uid),
                    (
                        "report_id",
                        "=",
                        report_id.id,
                    ),  # There will be no rules for report_id = False
                ],
                limit=1,
            )

            # Workstation printer
            workstation_printer_id = self.env.user._get_workstation_device(
                "printnode_workstation_printer_id"
            )

            # Priority:
            # 1. Printer from User Rules (if exists)
            # 2. Default Workstation Printer (User preferences)
            # 3. Default printer for current user (User Preferences)
            # 4. Default printer for current company (Settings)

            printer = (
                user_rules.printer_id
                or workstation_printer_id
                or self.env.user.printnode_printer
                or self.env.company.printnode_printer
            )
            printer_bin = (
                user_rules.printer_bin if user_rules.printer_id else printer.default_printer_bin
            )

            return printer, printer_bin

        return False, False

    @api.onchange("print_format")
    def _onchange_print_format(self):
        """
        Update printer based on selected report
        """
        self.printer_id = self._default_printer_id()

    def _is_dpc_enabled(self):
        """
        Returns True only if DPC enabled on the company level
        """
        return self.env.company.printnode_enabled

    def _prepare_report_data(self):
        if self.custom_quantity <= 0:
            raise UserError(_("You need to set a positive quantity."))
        if "green_card_zpl" in self.print_format:
            xml_id = "eurocable_stock.report_green_card"

        data = {
            "layout_wizard": self.id,
        }
        if self.stock_picking_id and self.label_line_ids:
            qties = defaultdict(int)
            for line in self.label_line_ids:
                qties[line.stock_move_line_id.id] += line.quantity
            # Pass only products with some quantity done to the report
            data["quantity_by_product"] = {p: int(q) for p, q in qties.items() if q}

        return xml_id, data

    def _check_quantity(self):
        for rec in self.label_line_ids:
            if rec.quantity < 1:
                raise ValidationError(
                    _("Quantity can not be less than 1 for line {product}").format(
                        **{
                            "product": rec.stock_move_line_id.product_id.name,
                        }
                    )
                )

    def process(self):
        self.ensure_one()

        self._check_quantity()

        # if no printer than download PDF
        # if not self.printer_id:
        #     self.with_context(download_only=True).process()

        xml_id, data = self._prepare_report_data()

        if not xml_id:
            raise UserError(_("Unable to find report template for %s format", self.print_format))

        return (
            self.env.ref(xml_id)
            .with_context(printer_id=self.printer_id.id, printer_bin=self.printer_bin.id)
            .report_action(None, data=data)
        )


class StockPickingLabelLayoutLine(models.TransientModel):
    _name = "stock.picking.label.layout.line"
    _description = "Choose the sheet layout to print the labels / Line"

    stock_move_line_id = fields.Many2one(
        comodel_name="stock.move.line",
        string="Stock move line",
    )

    quantity = fields.Integer(
        required=True,
        default=1,
    )

    wizard_id = fields.Many2one(
        comodel_name="stock.picking.label.layout",
    )
