# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Eurocable Stock',
    'version': '15.0.1.0.6',
    'author': 'Eezee-It',
    'category': 'Sale',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'product',
        'sale_stock',
        'delivery'
    ],
    'data': [
        'report/report_picking.xml',
        'report/report_delivery_document.xml',
        'views/stock_move_line_views.xml',
        'views/stock_picking_views.xml',
        'views/product_views.xml',
        'report/cart_green_paperformat.xml',
        'report/green_card_report_pdf.xml',
        'report/green_card_label.xml',
    ],
}
