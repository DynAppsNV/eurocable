from odoo import fields, models
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

MY_MODEL = "my.model"


class MyModel(models.Model):
    _inherit = "xx.system.option"
    _name = MY_MODEL
    _description = "My Model"
    _table = "my_model"

    name = fields.Char()


class SystemOption(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        MyModel._build_model(cls.registry, cls.env.cr)
        cls.registry.setup_models(cls.env.cr)
        cls.registry.init_models(cls.env.cr, [MY_MODEL], {"models_to_check": True})

        cls.foo = cls.env[MY_MODEL].create({"name": "Test My Model"})

    @classmethod
    # pylint: disable=W8110
    def tearDownClass(cls):
        super().tearDownClass()
        cls.registry.__delitem__(MyModel._name)

    def test_delete_non_system_option(self):
        self.foo.unlink()

    def test_delete_system_option(self):
        self.foo.xx_system_option = True
        with self.assertRaisesRegex(ValidationError, "A system option cannot be deleted"):
            self.foo.unlink()
