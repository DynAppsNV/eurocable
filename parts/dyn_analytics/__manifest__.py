{
    "name": "Odoo Analytics | Dynapps",
    "version": "17.0.1.0.0",
    "author": "dynapps",
    "license": "AGPL-3",
    "website": "https://www.dynapps.eu",
    "category": "Technical",
    "depends": ["web"],
    "data": [
        "data/cron.xml",
        "data/ir_config_parameter.xml",
        "security/ir.model.access.csv",
        "views/analytic.xml",
    ],
    "installable": True,
    "autoinstall": True,
    "post_init_hook": "post_init_hook",
}
