{
    "name": "Eurocable Account",
    "version": "17.0.0.1.3",
    "author": "dynapps",
    "category": "Account",
    "license": "LGPL-3",
    "depends": ["account", "eurocable_contacts", "eurocable_mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_fiscal_position.xml",
        "views/account_move_line_view.xml",
        "views/report_invoice.xml",
    ],
    "installable": True,
}
