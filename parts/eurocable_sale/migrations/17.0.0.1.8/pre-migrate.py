from odoo.tools.sql import column_exists, rename_column


def migrate(cr, version):
    if not version:
        return
    # The document type on products becomes company dependent. Keep the old
    # values aside so the post-migration can move them to the Eurocable company.
    if column_exists(cr, "product_template", "document_type_id"):
        rename_column(cr, "product_template", "document_type_id", "document_type_id_legacy")
