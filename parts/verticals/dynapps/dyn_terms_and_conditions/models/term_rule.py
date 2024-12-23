import base64
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from odoo.tools.safe_eval import safe_eval


class TermRule(models.Model):
    _name = "term.rule"
    _description = "Rules to define where the linked term is to be used."
    _order = "sequence asc, id"

    sequence = fields.Integer()
    term_id = fields.Many2one("term.term", "Term", required=True, ondelete="cascade")
    company_id = fields.Many2one("res.company", "Company")
    report_id = fields.Many2one("ir.actions.report", "Report", required=True)
    report_name = fields.Char(related="report_id.report_name", size=64)
    condition = fields.Char(size=128, help="condition on when to print the therm", required=True)

    def _get_terms_env(self, model):
        res_ids = self.env.context.get("res_ids")
        object_id = res_ids and res_ids[0] or False
        return {
            "object": self.env[model].browse(object_id),
            "report": self,
            "context": self.env.context,
        }

    @api.constrains("report_id", "condition")
    def check_condition(self):
        for record in self:
            try:
                safe_eval(self.condition, self._get_terms_env(record.report_id.model))
            except Exception as e:
                raise ValidationError(_("Incorrect condition specified: {}").format(e)) from e
        return True

    def _add_begin_terms(self, writer):
        self.ensure_one()
        att = PdfFileReader(BytesIO(base64.decodebytes(self.term_id.pdf)))
        writer.appendPagesFromReader(att)

    def _add_duplex_terms(self, writer):
        self.ensure_one()
        att = PdfFileReader(BytesIO(base64.decodebytes(self.term_id.pdf)))
        writer.appendPagesFromReader(att)

    def _add_txttoimg_terms(self, page):
        self.ensure_one()
        text = self.term_id.text
        fontsize = self.term_id.fontsize
        fontcolor = safe_eval(self.term_id.fontcolor)
        img_width = self.term_id.img_width
        img_height = self.term_id.img_height
        img_posx = self.term_id.img_posx
        img_posy = self.term_id.img_posy

        font_path = get_module_resource("dyn_terms_and_conditions", "fonts", self.term_id.font)
        font = ImageFont.truetype(font_path, fontsize)
        img = Image.new("RGBA", (img_width, img_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), text, fontcolor, font=font)
        img.save("%s.png" % text, "PNG")

        # Using ReportLab to insert image into PDF
        img_temp = BytesIO()
        img_doc = canvas.Canvas(img_temp)

        # Draw image on Canvas and save PDF in buffer
        img_path = "%s.png" % text
        img_doc.drawImage(img_path, img_posx, img_posy, img_width, img_height, mask="auto")
        img_doc.save()

        overlay = PdfFileReader(BytesIO(img_temp.getvalue())).getPage(0)
        page.mergePage(overlay)

    def _add_end_terms(self, writer):
        self.ensure_one()
        att = PdfFileReader(BytesIO(base64.decodebytes(self.term_id.pdf)))
        writer.appendPagesFromReader(att)

    def add_terms(self, pdf):
        writer = PdfFileWriter()
        # Add terms add the beginning
        for rule in self.filtered(lambda r: r.term_id.mode == "begin"):
            rule._add_begin_terms(writer)
        # Add terms at each page
        for page in PdfFileReader(BytesIO(pdf)).pages:
            rules = self.filtered(lambda r: r.term_id.mode in ("duplex", "txttoimg"))
            if rules:
                # Add terms on each page
                for rule in rules.filtered(lambda r: r.term_id.mode == "txttoimg"):
                    rule._add_txttoimg_terms(page)
                writer.addPage(page)
                # Add terms after each page
                for rule in rules.filtered(lambda r: r.term_id.mode == "duplex"):
                    rule._add_duplex_terms(writer)
            else:
                writer.addPage(page)
        # Add terms add the ending
        for rule in self.filtered(lambda r: r.term_id.mode == "end"):
            rule._add_end_terms(writer)

        pdf_content = BytesIO()
        writer.write(pdf_content)

        return pdf_content.getvalue()
