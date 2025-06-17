import re

from psycopg2.sql import SQL

from odoo import models


class IntrastatReportCustomHandler(models.AbstractModel):
    _inherit = "account.intrastat.report.handler"

    def _build_query(
        self,
        options,
        column_group_key=None,
        expanded_line_options=None,
        offset=0,
        limit=None,
        order_by=True,
        query_params=None,
    ):
        query, query_params = super()._build_query(
            options, column_group_key, expanded_line_options, offset, limit, order_by, query_params
        )
        # change query
        for block in filter(lambda b: isinstance(b, SQL), query.seq):
            block._wrapped = re.sub(
                r"(?<=COALESCE\()(prod\.weight)",
                "account_move_line.weight::numeric",
                block._wrapped,
            )
        return query, query_params
