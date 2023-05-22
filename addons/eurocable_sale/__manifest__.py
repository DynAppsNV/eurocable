# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Eurocable Sale',
    'version': '15.0.1.0.17',
    'author': 'Eezee-It',
    'category': 'Sale',
    'license': 'LGPL-3',
    'depends': [
        'sale_stock', 'smile_audit', 'base_location'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sales_wizard_views.xml',
        'wizard/sale_make_invoice_advance_views.xml',
        'views/sales_views.xml',
        'views/partner_views.xml',
        'views/product_template_view.xml',
        'views/document_type.xml',
        'data/template_certificate.xml',
        'report/certificat_report.xml',
        'report/sale_report_template.xml',
        'report/report_packing_list.xml'
    ],
}
