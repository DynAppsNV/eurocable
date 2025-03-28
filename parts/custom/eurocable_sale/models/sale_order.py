import base64

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_discount = fields.Monetary(
        compute="_compute_total_discount",
        readonly=False,
    )
    total_prices = fields.Monetary(
        compute="_compute_total_prices",
        readonly=False,
    )
    attachment_certification_ids = fields.Many2many(
        comodel_name="ir.attachment", domain="[('is_certificate', '=', True)]"
    )
    weight_total = fields.Float(default=0.0, compute="_compute_total_weight", store=True)

    # Description fields for stock.picking prints
    picking = fields.Char("Pakbon")
    picking_op_notes = fields.Char(
        string="Pakbon en prints",
        help="Information mentioned here will be "
        "visible in Picking operation document"
        " of transfer.",
    )
    delivery = fields.Char("Leverbon")
    delivery_notes = fields.Char(
        string="Leverbon en prints",
        help="Information mentioned here will be "
        "visible in delivery slip document "
        "of transfer.",
    )

    xx_same_client_order_ref_id = fields.Many2one(
        comodel_name="sale.order",
        string="Same Customer Reference",
        compute="_compute_xx_same_client_order_ref_id",
        compute_sudo=True,
    )

    @api.depends("order_line")
    def _compute_total_weight(self):
        for order in self:
            order.weight_total = sum(order.order_line.mapped("weight_total"))

    @api.depends("order_line")
    def _compute_total_prices(self):
        total_price = 0
        for rec in self:
            for order in rec.order_line:
                total_price += order.price_unit * order.product_uom_qty
            rec.total_prices = total_price

    @api.depends("order_line")
    def _compute_total_discount(self):
        total_discount = 0
        for order in self.order_line:
            total_discount += (order.price_unit * order.product_uom_qty) * (order.discount / 100)
        self.total_discount = round(total_discount, 2)

    @api.depends("client_order_ref", "company_id")
    def _compute_xx_same_client_order_ref_id(self):
        for order in self:
            client_order_ref = order.client_order_ref
            domain = [
                ("client_order_ref", "=", client_order_ref),
                ("id", "!=", order._origin.id),  # use _origin to deal with onchange()
            ]
            if company_id := order.company_id.id:
                domain += [("company_id", "in", (False, company_id))]
            order.xx_same_client_order_ref_id = client_order_ref and self.search(domain, limit=1)

    def action_confirm(self):
        show_warning = self._context.get("show_warning", False)
        if not self.partner_id.vat and not show_warning and not self.partner_id.is_not_vat:
            return {
                "name": "Warning",
                "type": "ir.actions.act_window",
                "res_model": "sales.wizard",
                "view_mode": "form",
                "view_type": "form",
                "target": "new",
                "context": {
                    "show_warning": True,
                },
            }
        res = super().action_confirm()
        for rec in self.filtered(lambda so: so.commitment_date):
            rec.picking_ids.filtered(lambda pick: pick.state not in ["done", "cancel"]).write(
                {
                    "date_done": rec.commitment_date,
                    "scheduled_date": rec.commitment_date,
                }
            )
        return res

    def print_certificate(self):
        self.ensure_one()
        report = self.env["ir.actions.report"]
        attachments = []
        attachment_obj = self.env["ir.attachment"]

        certif_template = self.env.ref("eurocable_sale.report_certification")

        for line in self.order_line:
            if line.product_id and not line.has_certificate:
                # Create certificates for each order line and make has_certificate True
                pdf_file, dummy = report._render_qweb_pdf(certif_template, line.ids)
                attachment = attachment_obj.create(
                    {
                        "name": "Certificate_" + line.product_id.name,
                        "datas": base64.b64encode(pdf_file),
                        "res_model": "sale.order",
                        "res_id": self.id,
                        "is_certificate": True,
                        "origin_id": line.id,
                        "type": "binary",
                    }
                )
                line.has_certificate = True
                attachments.append(attachment.id)
        if attachments:
            self.attachment_certification_ids = [(6, 0, attachments)]

    def send_certificate(self):
        self.ensure_one()

        template = self.env.ref("sale.email_template_edi_sale", False)

        self.print_certificate()

        compose_form = self.env.ref("mail.email_compose_message_wizard_form", False)
        ctx = dict(
            default_model="sale.order",
            default_res_ids=self.ids,
            default_template_id=template and template.id or False,
            default_composition_mode="comment",
            default_attachment_ids=self.attachment_certification_ids.ids,
        )
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }

    def _get_purchase_orders(self):
        procurement_groups = self.env["procurement.group"].search(
            [("sale_id", "=", self.id), ("id", "!=", self.procurement_group_id.id)]
        )
        return (
            super()._get_purchase_orders()
            | self.procurement_group_id.stock_move_ids.created_purchase_line_ids.order_id
            | self.procurement_group_id.stock_move_ids.move_orig_ids.purchase_line_id.order_id
            | procurement_groups.stock_move_ids.created_purchase_line_ids.order_id
            | procurement_groups.stock_move_ids.move_orig_ids.purchase_line_id.order_id
        )
