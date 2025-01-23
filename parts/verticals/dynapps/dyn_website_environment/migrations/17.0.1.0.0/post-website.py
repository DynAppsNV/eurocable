from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Migrate Basic Website data
    cr.execute("SELECT * FROM website")
    for row in cr.dictfetchall():
        website = env["website"].browse(row["id"])
        if not website:
            continue
        for field_name, _options in env["website"]._server_env_fields.items():
            if field_name in row:
                website[field_name] = row[field_name]
