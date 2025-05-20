from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    is_certificate = fields.Boolean(default=False)
    origin_id = fields.Many2one("sale.order.line")

    def unlink(self):
        for rec in self:
            rec.origin_id.has_certificate = False
        res = super().unlink()
        return res
