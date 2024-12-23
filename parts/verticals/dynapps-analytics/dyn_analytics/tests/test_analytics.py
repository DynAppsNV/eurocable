from unittest.mock import patch

import freezegun

from odoo.tests.common import HttpCase, TransactionCase


class TestAnalytics(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,  # no queue jobs
            )
        )
        cls.cron_publish_analytics = cls.env.ref("dyn_analytics.cron_publish_analytics")
        cls.env["ir.config_parameter"].set_param("dynapps_analytic_endpoint", "http://localhost")

    @freezegun.freeze_time("2024-02-06 16:00:00")
    def test_cron_publish_analytics(self):
        data = self.env["xx.dynapps.analytics"].prepare_analytic_data()
        # Mock the `requests` module and its `post` function
        with patch("requests.post") as mock_post:
            self.cron_publish_analytics.method_direct_trigger()
            mock_post.assert_called_once_with(
                self.env["ir.config_parameter"].get_param("dynapps_analytic_endpoint"),
                json=data,
                timeout=60,
            )

    def test_action(self):
        action = self.env["xx.dynapps.analytics"].action_open_view()
        self.assertEqual(action["xml_id"], "dyn_analytics.action_dynapps_analytics_form")
        self.assertEqual(action["res_model"], "xx.dynapps.analytics")
        self.assertTrue(action["res_id"])

    def test_formatted_json_data(self):
        self.assertTrue(self.env["xx.dynapps.analytics"].create({}).formatted_json_data)


class TestAnalyticsController(HttpCase):
    def test_json(self):
        self.url_open(
            "/.dynapps/analytics", headers={"Content-Type": "application/json"}, data="{}"
        )
