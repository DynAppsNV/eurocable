# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models, api
import base64


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
    attachment_certification_ids = fields.Many2many('ir.attachment',
                                                    domain="[('is_certificate', '=', True)]")
    weight_total = fields.Float(
        default=0.0,
        compute="_compute_total_weight",
        store=True)

    # Description fields for stock.picking prints
    picking = fields.Char('Pakbon')
    picking_op_notes = fields.Char('Pakbon en prints',
                                   help="Information mentioned here will be "
                                        "visible in Picking operation document"
                                        " of transfer.")
    delivery = fields.Char('Leverbon')
    delivery_notes = fields.Char('Leverbon en prints',
                                 help='Information mentioned here will be '
                                      'visible in delivery slip document '
                                      'of transfer.')

    @api.depends("order_line")
    def _compute_total_weight(self):
        for line in self:
            line.weight_total = sum(line.order_line.mapped('weight_total'))

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

    def action_confirm(self):
        show_warning = self._context.get('show_warning', False)
        if not self.partner_id.vat and not show_warning and not self.partner_id.is_not_vat:
            return {
                'name': 'Warning',
                'type': 'ir.actions.act_window',
                'res_model': 'sales.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {
                    'show_warning': True,
                }
            }
        return super(SaleOrder, self).action_confirm()

    def print_certificate(self):
        self.ensure_one()
        attachments = []
        attachment_obj = self.env['ir.attachment']

        certif_template = self.env.ref('eurocable_sale.report_certification')

        for line in self.order_line:
            if line.product_id and not line.has_certificate:
                """Create certificates for each order line and make has_certificate True"""
                pdf_file, dummy = certif_template._render_qweb_pdf(line.id)
                attachment = attachment_obj.create({
                    'name': 'Certificate_' + line.product_id.name,
                    'datas': base64.b64encode(pdf_file),
                    'res_model': 'sale.order',
                    'res_id': self.id,
                    'is_certificate': True,
                    'origin_id': line.id,
                    'type': 'binary',
                })
                line.has_certificate = True
                attachments.append(attachment.id)
        if attachments:
            self.attachment_certification_ids = [(6, 0, attachments)]

    def send_certificate(self):
        self.ensure_one()

        template = self.env.ref('sale.email_template_edi_sale', False)

        self.print_certificate()

        compose_form = self.env.ref("mail.email_compose_message_wizard_form", False)
        ctx = dict(
            default_model="sale.order",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            default_attachment_ids=self.attachment_certification_ids.ids,
        )
        return {
            "name": ("Compose Email"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }
