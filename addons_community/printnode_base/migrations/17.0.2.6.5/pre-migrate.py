from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """rename test_types"""
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    if env.ref("printnode_base.menu_printnode_general", raise_if_not_found=False):
        env.ref("printnode_base.menu_printnode_general", raise_if_not_found=False).unlink()
    if env.ref("printnode_base.printnode_config_action", raise_if_not_found=False):
        env.ref("printnode_base.printnode_config_action", raise_if_not_found=False).unlink()
    if env.ref("printnode_base.res_config_settings_view_form", raise_if_not_found=False):
        env.ref("printnode_base.res_config_settings_view_form", raise_if_not_found=False).unlink()
