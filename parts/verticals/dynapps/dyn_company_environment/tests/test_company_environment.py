from odoo.addons.server_environment.tests.common import ServerEnvironmentCase

company_config = """
[res.company]
primary_color = #AAAAAA

[res.company.MAIN]
primary_color = #BBBBBB

[res.company.OTHER]
primary_color = #CCCCCC
"""


class TestCompanyEnvironment(ServerEnvironmentCase):
    def test_company_settings(self):
        company1 = self.env["res.company"].create({"name": "Company 1", "code": "MAIN"})
        company2 = self.env["res.company"].create({"name": "Company 2", "code": "OTHER"})
        company3 = self.env["res.company"].create({"name": "Company 3"})
        with self.load_config(public=company_config):
            self.assertEqual(company1.primary_color, "#BBBBBB")
            self.assertEqual(company2.primary_color, "#CCCCCC")
            self.assertEqual(company3.primary_color, "#AAAAAA")
