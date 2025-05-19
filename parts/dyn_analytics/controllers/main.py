import json

from odoo import SUPERUSER_ID, _, http
from odoo.exceptions import AccessError
from odoo.http import Response


class DynappsAnalyticController(http.Controller):
    @http.route("/.dynapps/analytics", auth="user")
    def main(self, **kwargs):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("Access denied"))
        env = http.request.env(user=SUPERUSER_ID).with_context(lang="en_US")
        data = env["xx.dynapps.analytics"].prepare_analytic_data()
        return Response(json.dumps(data), headers={"Content-Type": "application/json"})
