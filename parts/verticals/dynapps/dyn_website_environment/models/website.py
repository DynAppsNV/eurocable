import operator

from odoo import api, fields, models
from odoo.osv.expression import FALSE_DOMAIN


class Website(models.Model):
    _name = "website"
    _inherit = ["website", "server.env.mixin"]
    _server_env_section_name_field = "code"

    code = fields.Char()
    domain = fields.Char(search="_search_website_domain")
    name = fields.Char(search="_search_website_name")

    @api.model
    def _search_website_domain(self, oper, value):
        """Keep the domain field searchable to allow domain in search view."""
        operators = {
            "=": operator.eq,
            "!=": operator.ne,
            "in": operator.contains,
            "not in": lambda a, b: not operator.contains(a, b),
            "ilike": lambda a, b: operator.contains(b, a),
            "not ilike": lambda a, b: not operator.contains(b, a),
        }
        if oper not in operators:
            return FALSE_DOMAIN
        websites = self.search([]).filtered(lambda w: operators[oper](value, w.domain or ""))
        return [("id", "in", websites.ids)]

    @api.model
    def _search_website_name(self, oper, value):
        """Keep the name field searchable to allow name in search view."""
        operators = {
            "=": operator.eq,
            "!=": operator.ne,
            "in": operator.contains,
            "not in": lambda a, b: not operator.contains(a.lower(), b.lower()),
            "ilike": lambda a, b: operator.contains(b.lower(), a.lower()),
            "not ilike": lambda a, b: not operator.contains(b.lower(), a.lower()),
        }
        if oper not in operators:
            return FALSE_DOMAIN
        websites = self.search([]).filtered(
            lambda w: operators[oper](value.lower(), (w.name or "").lower())
        )
        return [("id", "in", websites.ids)]

    @property
    def _server_env_fields(self):
        base_fields = super()._server_env_fields
        website_fields = {
            "name": {},
            "domain": {},
        }
        base_fields.update(website_fields)
        return base_fields

    @api.model
    def _server_env_global_section_name(self):
        """Name of the global section in the configuration files"""
        return "website"
