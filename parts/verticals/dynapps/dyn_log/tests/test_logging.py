import logging
from datetime import datetime
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo.tests import common
from odoo.tools import config, mute_logger

from ..models.db_handler import (
    LEVEL_CRITICAL,
    LEVEL_DEBUG,
    LEVEL_ERROR,
    LEVEL_INFO,
    LEVEL_WARNING,
    DBHandler,
    DBLogger,
)


class TestSetup(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.log_obj = cls.env["xx.log"]
        cls.db_logger = DBLogger(cls.cr, "xx.log.test", 0, cls.env.uid)

    @staticmethod
    def _set_handler(level):
        with patch.object(config, "options", {**config.options, "log_level": level}):
            logger = logging.getLogger("xx_log")
            logger.handlers = []
            logger.addHandler(DBHandler())

    @mute_logger("xx_log")
    def test_001_debug(self):
        self._set_handler("debug")
        self.db_logger.debug("Test Debugging")
        log = self.log_obj.search([("message", "like", "Test Debugging")])
        self.assertTrue(log.level, LEVEL_DEBUG)

    def test_002_info(self):
        self.db_logger.info("Test Info")
        log = self.log_obj.search([("message", "=", "Test Info")])
        self.assertTrue(log.user_name)
        self.assertTrue(log.res_name)
        self.assertTrue(log.level, LEVEL_INFO)

    @mute_logger("xx_log")
    def test_003_warning(self):
        self._set_handler("warn")
        self.db_logger.warning("Test Warning")
        log = self.log_obj.search([("message", "=", "Test Warning")])
        self.assertTrue(log.level, LEVEL_WARNING)

    @mute_logger("xx_log")
    def test_004_error(self):
        self._set_handler("error")
        self.db_logger.error("Test Error")
        log = self.log_obj.search([("message", "=", "Test Error")])
        self.assertTrue(log.level, LEVEL_ERROR)

    @mute_logger("xx_log")
    def test_005_exception(self):
        self._set_handler("error")
        try:
            _ = 1 / 0
        except ZeroDivisionError:
            self.db_logger.exception("Test Exception")
        log = self.log_obj.search([("message", "like", "Test Exception")])
        self.assertTrue(log.level, LEVEL_CRITICAL)
        self.assertRegex(log.message, r"Traceback[\s\S]*?ZeroDivisionError")

    @mute_logger("xx_log")
    def test_006_critical(self):
        self._set_handler("critical")
        try:
            _ = 1 / 0  # pylint: disable-all
        except ZeroDivisionError:
            self.db_logger.critical("Test Critical")
        log = self.log_obj.search([("message", "like", "Test Critical")])
        self.assertTrue(log.level, LEVEL_CRITICAL)
        self.assertRegex(log.message, r"Traceback[\s\S]*?ZeroDivisionError")

    @mute_logger("xx_log")
    def test_007_debug_timed(self):
        self._set_handler("debug")
        self.db_logger.time_debug("Test Timed Debugging")
        log = self.log_obj.search([("message", "like", "Test Timed Debugging")])
        self.assertTrue(log.level, LEVEL_DEBUG)

    def test_008_info_timed(self):
        self.db_logger.time_info("Test Timed Info")
        log = self.log_obj.search([("message", "like", "Test Timed Info")])
        self.assertTrue(log.user_name)
        self.assertTrue(log.res_name)
        self.assertTrue(log.level, LEVEL_INFO)

    @mute_logger("xx_log")
    def test_009_pid(self):
        self.assertTrue(self.db_logger.pid)

    def test_010_cleanup(self):
        self.db_logger.info("Test Info")
        log = self.log_obj.search([("message", "=", "Test Info")])
        self.assertTrue(log)
        self.log_obj.scheduled_cleanup()
        self.assertTrue(log.exists())
        with freeze_time(datetime.today().date() + relativedelta(months=+1)):
            self.log_obj.scheduled_cleanup()
        self.assertTrue(log.exists())
        with freeze_time(datetime.today().date() + relativedelta(months=+1, days=+1)):
            self.log_obj.scheduled_cleanup()
        self.assertFalse(log.exists())

    def test_011_log_model(self):
        db_logger = DBLogger(
            self.cr,
            "res.company",
            self.env.ref("base.main_company").id,
            self.env.ref("base.user_admin").id,
        )
        db_logger.info("Test Info")
        log = self.log_obj.search([("message", "=", "Test Info")])
        self.assertTrue(log)
        self.assertEqual(log.uid, self.env.ref("base.user_admin").id)
        self.assertEqual(log.model_name, "res.company")
        self.assertEqual(log.res_id, self.env.ref("base.main_company").id)
        self.assertEqual(log.res_name, self.env.ref("base.main_company").name)
        db_logger.info("Test Info2")
        log2 = self.log_obj.search([("message", "=", "Test Info2")])
        db_logger.info("Test Info3")
        log3 = self.log_obj.search([("message", "=", "Test Info3")])
        (log2 + log3).mapped("res_name")
