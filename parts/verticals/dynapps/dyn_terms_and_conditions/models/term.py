from odoo import fields, models


class TermTerm(models.Model):
    _name = "term.term"
    _description = "Terms and conditions"

    name = fields.Char(size=64, required=True)
    pdf = fields.Binary(string="PDF File", help="The PDF file to attach to the report")
    mode = fields.Selection(
        selection=[
            ("begin", "Before report"),
            ("end", "After report"),
            ("duplex", "Every other page"),
            ("txttoimg", "Text to Image"),
        ],
        string="Insertion mode",
        required=True,
    )
    term_rule_ids = fields.One2many(
        comodel_name="term.rule",
        inverse_name="term_id",
        string="Uses",
        help="reports where the term is used",
    )
    text = fields.Char()
    font = fields.Selection(
        selection=[
            ("FreeMono.ttf", "FreeMono"),
            ("FreeMonoBold.ttf", "FreeMonoBold"),
            ("FreeMonoBoldOblique.ttf", "FreeMonoBoldOblique"),
            ("FreeMonoOblique.ttf", "FreeMonoOblique"),
            ("FreeSans.ttf", "FreeSans"),
            ("FreeSansBold.ttf", "FreeSansBold"),
            ("FreeSansBoldOblique.ttf", "FreeSansBoldOblique"),
            ("FreeSansOblique.ttf", "FreeSansOblique"),
            ("FreeSerif.ttf", "FreeSerif"),
            ("FreeSerifBold.ttf", "FreeSerifBold"),
            ("FreeSerifBoldItalic.ttf", "FreeSerifBoldItalic"),
            ("FreeSerifItalic.ttf", "FreeSerifItalic"),
        ],
        default="FreeMono.ttf",
    )
    fontcolor = fields.Selection(
        [("(0,0,0)", "Black"), ("(255,0,0)", "Red"), ("(0,255,0)", "Green"), ("(0,0,255)", "Blue")],
        string="Font color",
        default="(0,0,0)",
    )
    fontsize = fields.Integer(default=24)
    img_width = fields.Integer(string="Width", default=132)
    img_height = fields.Integer(string="Height", default=28)
    img_posx = fields.Integer(string="Pos X", default=28)
    img_posy = fields.Integer(string="Pos Y", default=710)
