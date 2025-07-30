from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})

    query = """
        UPDATE ir_ui_view
        SET arch_db = arch_db - 'fr_BE' - 'nl_BE'
        WHERE key = 'eurocable_sale.report_order_inherit_discount';
    """
    env.cr.execute(query)
