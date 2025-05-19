# -*- coding: utf-8 -*-
{
    "name": "SW - SO Invoicing No Merge",
    "summary": "Choose whether to merge multiple sale orders into one invoice or invoice them separately.",
    "description": """
        This module grants the user the choice to whether consolidate multiple sales orders in one invoice
        or note when selecting them in the Orders To Invoice page.
        """,
    "author": "Smart Way Business Solutions",
    "website": "https://www.smartway.co",
    "category": "Accounting",
    "version": "17.0.0.0.0",
    "depends": ["base", "sale"],
    "data": [
        "wizard/sale_make_invoice_advance_views.xml",
    ],
    "images": ["static/description/image.png"],
    "license": "Other proprietary",
}
