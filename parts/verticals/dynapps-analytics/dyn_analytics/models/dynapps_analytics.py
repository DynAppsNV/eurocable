import json

import requests

from odoo import fields, models, service

DATA_SCHEMA_VERSION = "1.0"


class DynappsAnalytics(models.TransientModel):
    _name = "xx.dynapps.analytics"
    _description = "Dynapps Analytics"

    name = fields.Char(default="Dynapps Analytics")
    formatted_json_data = fields.Text(compute="_compute_json_data", compute_sudo=True)

    def _compute_json_data(self):
        for rec in self:
            rec.formatted_json_data = json.dumps(self.prepare_analytic_data(), indent=4)

    def _cron_publish_analytics(self):
        endpoint = self.env["ir.config_parameter"].get_param("dynapps_analytic_endpoint")
        data = self.prepare_analytic_data()
        requests.post(endpoint, json=data, timeout=60)

    def prepare_analytic_data(self):
        self_lang = self.with_context(lang="en_US")
        get_param = self_lang.env["ir.config_parameter"].get_param
        all_modules = self_lang.env["ir.module.module"].search([])
        version_info = service.common.exp_version()
        data = {
            "data_schema_version": DATA_SCHEMA_VERSION,
            "create_timestamp": fields.Datetime.now().isoformat(),
            "database_name": self_lang.env.cr.dbname,
            "database_uuid": get_param("database.uuid", None),
            "database_expiration": get_param("database.expiration_date", None),
            "buildout_version": get_param("buildout.db_version", None),
            "internal_users": self_lang.env["res.users"].search_count([("share", "=", False)]),
            "public_users": self_lang.env["res.users"].search_count([("share", "=", True)]),
            "odoo_version": version_info.get("server_serie"),
            "company_count": self_lang.env["res.company"].search_count([]),
            "web_base_url": get_param("web.base.url", None),
            "modules": {},
        }
        for module in all_modules:
            module_data = {
                "state": module.state,
                "author": module.author if module.author is not False else None,
                "installed_version": module.latest_version,
                "disk_version": module.installed_version,
                "dependencies": module.dependencies_id.mapped("name"),
                "shortdesc": module.shortdesc if module.shortdesc is not False else None,
                "website": module.website if module.website is not False else None,
                "category": module.category_id.name,
            }
            data["modules"][module.name] = module_data
        return data

    def action_open_view(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "dyn_analytics.action_dynapps_analytics_form"
        )
        analytic_id = self.sudo().create({})
        action["res_id"] = analytic_id.id
        return action
