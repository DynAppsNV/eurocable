from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})

    for record in env["mrp.production"].search(["user_id", "=", False]):
        record.user_id = record.write_uid
