from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Remove the default value on the field `to_check` of `account.move`,
    # it is not needed anymore
    env["ir.default"].search(
        [("field_id", "=", env.ref("account.field_account_move__to_check").id)]
    ).unlink()
