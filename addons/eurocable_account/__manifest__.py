# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Eurocable Account',
    'version': '15.0.1.0.17',
    'author': 'Eezee-It',
    'category': 'Account',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'account_followup',
        'account_intrastat',
        'account_reports',
        'eurocable_contacts'
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/account_move_line_view.xml",
        "views/account_fiscal_position.xml",
        "views/intrastat_report.xml",
        'views/account_financial_report.xml',
        'views/report_financial.xml',
        'views/account_move.xml',
        'views/report_invoice.xml',
        'views/partner_views.xml'
    ],
    "installable": True,
}
