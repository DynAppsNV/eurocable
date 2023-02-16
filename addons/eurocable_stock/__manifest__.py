# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Eurocable Stock',
    'version': '15.0.1.0.6',
    'author': 'Eezee-It',
    'category': 'Sale',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'stock',
        'product',
        'sale_stock',
        'delivery',
        'printnode_base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/report_picking.xml',
        'report/report_delivery_document.xml',
        'views/stock_move_line_views.xml',
        'views/stock_picking_views.xml',
        'views/product_views.xml',
        'report/green_card_label.xml',
        'views/res_company_view.xml',
        'views/stock_picking_label_layout_views.xml'
    ],
}
