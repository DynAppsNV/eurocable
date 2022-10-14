# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Eurocable Sale',
    'version': '15.0.1.0.4',
    'author': 'Eezee-It',
    'category': 'Sale',
    'license': 'LGPL-3',
    'depends': [
        'sale', 'smile_audit'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sales_wizard_views.xml',
        'views/sales_views.xml',
        'views/partner_views.xml',
        'report/sale_report_template.xml'
    ],
}
