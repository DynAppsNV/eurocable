from odoo import models, fields


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    is_certificate = fields.Boolean(default=False)
    origin_id = fields.Many2one("sale.order.line")

    def unlink(self):
        for rec in self:
            rec.origin_id.has_certificate = False
        res = super(IrAttachment, self).unlink()
        return res
