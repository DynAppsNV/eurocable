import re

from odoo import models


class IntrastatReportCustomHandler(models.AbstractModel):
    _inherit = "account.intrastat.report.handler"

    def _build_query(
        self, options, column_group_key=None, expanded_line_options=None, offset=0, limit=None
    ):
        query, query_params = super()._build_query(
            options, column_group_key, expanded_line_options, offset, limit
        )
        # change query
        query["select"] = re.sub(
            r"(?<=COALESCE\()(prod)(?=.weight)", "account_move_line", query["select"]
        )
        return query, query_params
