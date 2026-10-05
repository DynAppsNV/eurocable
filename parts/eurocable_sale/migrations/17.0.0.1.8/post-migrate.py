from odoo import SUPERUSER_ID, api
from odoo.tools.sql import column_exists


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    eurocable = env.ref("base.main_company")

    # Existing certifications contain Eurocable specific texts
    cr.execute(
        "UPDATE document_type SET company_id = %s WHERE company_id IS NULL",
        (eurocable.id,),
    )

    if not column_exists(cr, "product_template", "document_type_id_legacy"):
        return
    cr.execute(
        """
        SELECT id, document_type_id_legacy
        FROM product_template
        WHERE document_type_id_legacy IS NOT NULL
        """
    )
    if values := dict(cr.fetchall()):
        env["ir.property"].with_company(eurocable)._set_multi(
            "document_type_id", "product.template", values
        )
    cr.execute("ALTER TABLE product_template DROP COLUMN document_type_id_legacy")
