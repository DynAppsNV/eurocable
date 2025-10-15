import json
from datetime import datetime

import responses
from freezegun import freeze_time

from odoo import service
from odoo.tests.common import HttpCase, TransactionCase
from odoo.tools import mute_logger

MOCK_BASE_URL = "http://localhost"


class TestAnalytics(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Analytics = cls.env["xx.dynapps.analytics"]
        cls.get_param = cls.env["ir.config_parameter"].sudo().get_param
        cls.env["ir.config_parameter"].sudo().set_param("dynapps_analytic_endpoint", MOCK_BASE_URL)
        cls.version_info = service.common.exp_version()

    def test_analytics_sending(self):
        action = self.Analytics.action_open_view()
        self.assertEqual(action["res_id"], self.Analytics.search([], limit=1, order="id desc").id)
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["views"], [(False, "form")])
        self.assertEqual(action["target"], "current")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], "Dynapps Analytics")
        self.assertEqual(action["res_model"], "xx.dynapps.analytics")
        analytics = self.Analytics.browse(action["res_id"])
        self.assertTrue(analytics)
        analytics_json = json.loads(analytics.formatted_json_data)
        self.assertTrue(analytics_json)
        self.assertIn("odoo_version", analytics_json)
        self.assertIn("database_uuid", analytics_json)
        self.assertIn("modules", analytics_json)
        self.assertIsInstance(analytics_json["modules"], dict)
        self.assertIn("dyn_analytics", analytics_json["modules"])
        self.assertNotIn("detailed_statistics", analytics_json)

    @responses.activate
    @mute_logger("odoo.sql_db")
    def test_analytics_fetch_details(self):
        # Mock the get_data_to_fetch response
        responses.add(
            responses.POST,
            f"{MOCK_BASE_URL}/get_data_to_fetch",
            json={
                "result": {
                    "base": [
                        {
                            "report_as": "user_info",
                            "query": "SELECT count(1), min(id) from res_users",
                        },
                        {
                            "report_as": "invalid_query",
                            "query": "SELECT count(1), min(id) from non_existing_table",
                        },
                    ],
                }
            },
            status=200,
        )
        self.env["ir.config_parameter"].sudo().set_param("dynapps_analytic_fetch_details", "True")
        action = self.Analytics.action_open_view()
        analytics = self.Analytics.browse(action["res_id"])
        analytics_json = json.loads(analytics.formatted_json_data)
        self.assertIn("detailed_statistics", analytics_json)
        self.env.cr.execute("SELECT count(1), min(id) from res_users")
        self.assertEqual(
            analytics_json["detailed_statistics"]["user_info"][0], self.env.cr.dictfetchall()[0]
        )
        self.assertIn("invalid_query", analytics_json["detailed_statistics"])
        self.assertIn(
            'relation "non_existing_table" does not exist',
            analytics_json["detailed_statistics"]["invalid_query"],
        )

    @responses.activate
    @freeze_time(datetime.now())
    def test_cron(self):
        analytics = self.Analytics.create({})
        # Mock the post data call
        resp_post = responses.add(
            responses.POST,
            f"{MOCK_BASE_URL}",
            body="one",
            match=[
                responses.matchers.json_params_matcher(json.loads(analytics.formatted_json_data))
            ],
            status=200,
        )
        self.Analytics._cron_publish_analytics()
        self.assertEqual(resp_post.call_count, 1)

    @responses.activate
    def test_cron_publish_analytics_empty_url(self):
        self.env["ir.config_parameter"].set_param("dynapps_analytic_endpoint", "False")
        analytics = self.Analytics.create({})
        # Mock the post data call
        resp_post = responses.add(
            responses.POST,
            f"{MOCK_BASE_URL}",
            body="one",
            match=[
                responses.matchers.json_params_matcher(json.loads(analytics.formatted_json_data))
            ],
            status=200,
        )
        self.Analytics._cron_publish_analytics()
        self.assertEqual(resp_post.call_count, 0)


class TestAnalyticsController(HttpCase):
    def test_json(self):
        self.authenticate("admin", "admin")
        body = json.dumps({})
        response = self.url_open("/.dynapps/analytics", data=body)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("odoo_version", payload)
        self.assertIn("database_uuid", payload)
        self.assertIn("modules", payload)
        self.assertIsInstance(payload["modules"], dict)
        self.assertIn("dyn_analytics", payload["modules"])

    def test_json_access_denied(self):
        self.authenticate("demo", "demo")
        headers = {
            "Content-Type": "application/json",
        }
        body = json.dumps({})

        response = self.url_open("/.dynapps/analytics", headers=headers, data=body)
        self.assertEqual(response.status_code, 403)
