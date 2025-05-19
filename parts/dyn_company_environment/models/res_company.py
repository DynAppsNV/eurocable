from odoo import api, models, tools


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "server.env.mixin"]

    _server_env_section_name_field = "code"

    @property
    def _server_env_fields(self):
        base_fields = super()._server_env_fields
        # Added for testing purposes
        if tools.config.get("test_enable"):
            base_fields.update({"primary_color": {}})
        return base_fields

    @api.model
    def _server_env_global_section_name(self):
        """Name of the global section in the configuration files"""
        return "res.company"
