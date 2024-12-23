def migrate(cr, version):
    if not version:
        return

    cr.execute(
        """
UPDATE res_partner SET sale_warn='no-message'WHERE sale_warn is null;
UPDATE res_partner SET picking_warn='no-message'WHERE picking_warn is null;
UPDATE res_partner SET purchase_warn='no-message'WHERE purchase_warn is null;
UPDATE res_partner SET invoice_warn='no-message'WHERE invoice_warn is null;
"""
    )
