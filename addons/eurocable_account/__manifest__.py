# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Eurocable Account',
    'version': '15.0.1.0.0',
    'author': 'Eezee-It',
    'category': 'Account',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'account_reports',
    ],
    'data': [
        'data/account_financial_report_data.xml',
        'views/report_financial.xml',
        'views/account_move.xml',
    ],
}
