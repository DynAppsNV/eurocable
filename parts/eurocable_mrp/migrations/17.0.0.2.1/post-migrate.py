from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})

    for record in env["mrp.production"].search(
        [("user_id", "=", False), ("create_date", ">=", "2026-01-01 00:00:00")]
    ):
        record.user_id = record.write_uid.id
