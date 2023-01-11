# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Eurocable Account',
    'version': '15.0.1.0.10',
    'author': 'Eezee-It',
    'category': 'Account',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'account_reports',
        'account_intrastat',
    ],
    'data': [
        "views/account_move_line_view.xml",
        "views/account_fiscal_position.xml",
        "views/intrastat_report.xml",
        'views/account_financial_report.xml',
        'views/report_financial.xml',
        'views/account_move.xml',
        'views/report_invoice.xml',
    ],
    "installable": True,
}
