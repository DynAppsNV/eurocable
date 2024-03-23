from odoo.upgrade import util


def migrate(cr, version):
    """Set removal strategy on product categories"""
    if not version:
        return

    # REMOVE REDUNDANT XML ID
    XML_IDS = [
        "eurocable_contacts.view_partner_form_inherit",
        "eurocable_sale.view_partner_form_inherit",
    ]
    for xml_id in XML_IDS:
        util.remove_view(cr, xml_id=xml_id)

    # REMOVE FIELDS
    util.remove_field(cr, "res.partner", "send_so_to_inv", drop_column=True)
