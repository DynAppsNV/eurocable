from odoo import SUPERUSER_ID, api
from odoo.tools import SQL


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})

    query = """
        UPDATE ir_model_fields
        SET field_description = field_description - 'fr_BE' - 'nl_BE'
        WHERE model = 'mrp.production' and name = 'xx_weight';
    """
    env.cr.execute(SQL(query))
