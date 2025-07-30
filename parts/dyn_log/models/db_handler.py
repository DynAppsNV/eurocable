import logging
import traceback
from datetime import datetime

from dateutil import relativedelta

import odoo
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

LEVEL_DEBUG = "DEBUG"
LEVEL_INFO = "INFO"
LEVEL_WARNING = "WARNING"
LEVEL_ERROR = "ERROR"
LEVEL_CRITICAL = "CRITICAL"


class DBHandler(logging.Handler):
    def __init__(self):
        level = LEVEL_INFO
        if tools.config["log_level"] == "info":
            level = LEVEL_INFO
        elif tools.config["log_level"] in (
            "debug",
            "debug_rpc",
            "debug_rpc_answer",
            "debug_sql",
        ):
            level = LEVEL_DEBUG
        elif tools.config["log_level"] == "warn":
            level = LEVEL_WARNING
        elif tools.config["log_level"] == "error":
            level = LEVEL_ERROR
        elif tools.config["log_level"] == "critical":
            level = LEVEL_CRITICAL

        level = getattr(logging, level, logging.INFO)
        logger = logging.getLogger("xx_log")
        logger.setLevel(level)

        logging.Handler.__init__(self, level)
        self._dbname_to_cr = {}
        self._test_enable = False

    # pylint: disable=protected-access
    def _get_cursor(self, dbname):
        _cr = self._dbname_to_cr.get(dbname)
        # Last part checks if the connection to the database is still open.
        # This is needed when dyn_log is used in cron jobs. If there are multiple databases, the
        # connection to the database is closed with each cron job execution. If this is the case,
        # the cursor of the logger doesn't work anymore, and should be re-initiated.
        if not _cr or (_cr and _cr.closed) or (_cr and _cr._cnx.closed):
            registry = odoo.registry(dbname)
            _cr = registry.cursor()
            self._dbname_to_cr[dbname] = _cr
        return _cr

    def emit(self, record):
        if not (record.args and isinstance(record.args, dict)):
            return False
        self._test_enable = record.args.get("test_enable", "")

        _cr = record.args.get("cr")
        dbname = _cr.dbname
        if not self._test_enable:
            _cr = self._get_cursor(dbname)
        else:
            self._dbname_to_cr[dbname] = _cr

        res_id = record.args.get("res_id") or 0
        pid = record.args.get("pid") or 0
        uid = record.args.get("uid") or 0
        model_name = record.args.get("model_name") or ""

        request = """INSERT
                       INTO xx_log (date, uid, model_name, res_id, pid, level, message)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)
                  """
        date = datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
        params = (date, uid, model_name, res_id, pid, record.levelname, record.msg)

        # pylint: disable=broad-except
        try:
            _cr.execute(request, params)
        except Exception:
            if not self._test_enable:
                # retry
                try:
                    _cr = self._get_cursor(dbname)
                    _cr.execute(request, params)
                except Exception:
                    # pylint: disable=print-used
                    print(f"Failed to log into xx_log {model_name} {res_id} {record}")

        if not self._test_enable:
            _cr.commit()
        return True

    def close(self):
        logging.Handler.close(self)
        for _cr in self._dbname_to_cr.values():
            if not _cr:
                continue
            if not self._test_enable:
                _cr = self._get_cursor(_cr.dbname)
            try:
                request = """INSERT
                               INTO xx_log (date, uid, model_name, res_id, pid, level, message)
                             VALUES (%s, %s, %s, %s, %s, %s, %s)
                          """
                date = datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
                params = (date, 0, "", 0, 0, LEVEL_INFO, "Odoo server stopped")
                try:
                    _cr.execute(request, params)
                # pylint: disable=broad-except
                except Exception:
                    # pylint: disable=print-used
                    print("Odoo server stopped")
                if not self._test_enable:
                    _cr.commit()
            finally:
                if not self._test_enable:
                    _cr.close()
        self._dbname_to_cr = {}


def add_timing(original_method):
    def new_method(self, msg):
        # pylint: disable=protected-access
        delay = relativedelta.relativedelta(datetime.now(), self._logger_start)
        msg += (
            f" after {delay.hours}h {delay.minutes}min "
            f"{delay.seconds}.{str(delay.microseconds).zfill(6)}s"
        )
        return original_method(self, msg)

    return new_method


def add_trace(original_method):
    def new_method(self, msg):
        stack = traceback.format_exc()
        msg += "\n%s" % stack
        return original_method(self, msg)

    return new_method


class DBLogger:
    def __init__(self, cr, model_name, res_id, uid=0):
        assert isinstance(uid, int), "uid should be an integer"
        self._logger = logging.getLogger("xx_log")

        test_enable = odoo.tools.config["test_enable"]
        if not test_enable:
            registry = odoo.registry(cr.dbname)
        self._cr = cr
        try:
            if not test_enable:
                self._cr = registry.cursor()
            self._cr.execute("select nextval('xx_log_seq')")
            res = self._cr.fetchone()
            pid = res[0] if res else 0
        finally:
            if not test_enable and self._cr:
                self._cr.close()

        self._logger_start = datetime.now()
        self._logger_args = {
            "model_name": model_name,
            "res_id": res_id,
            "uid": uid,
            "pid": pid,
            "test_enable": test_enable,
            "cr": self._cr,
        }

    @property
    def pid(self):
        return self._logger_args["pid"]

    def debug(self, msg):
        msg = msg.replace("%", "%%")
        self._logger.debug(msg, self._logger_args)

    def info(self, msg):
        msg = msg.replace("%", "%%")
        self._logger.info(msg, self._logger_args)

    def warning(self, msg):
        msg = msg.replace("%", "%%")
        self._logger.warning(msg, self._logger_args)

    def error(self, msg):
        msg = msg.replace("%", "%%")
        self._logger.error(msg, self._logger_args)

    @add_trace
    def critical(self, msg):
        msg = msg.replace("%", "%%")
        self._logger.critical(msg, self._logger_args)

    @add_trace
    def exception(self, msg):
        msg = msg.replace("%", "%%")
        self._logger.exception(msg, self._logger_args)

    @add_timing
    def time_info(self, msg):
        msg = msg.replace("%", "%%")
        self._logger.info(msg, self._logger_args)

    @add_timing
    def time_debug(self, msg):
        msg = msg.replace("%", "%%")
        self._logger.debug(msg, self._logger_args)


logging.getLogger("xx_log").addHandler(DBHandler())
