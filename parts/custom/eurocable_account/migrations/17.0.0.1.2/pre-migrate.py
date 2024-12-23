from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    if intrastat_view := env.ref(
        "account_intrastat.report_invoice_document_intrastat_2019", raise_if_not_found=False
    ):
        intrastat_view.unlink()
