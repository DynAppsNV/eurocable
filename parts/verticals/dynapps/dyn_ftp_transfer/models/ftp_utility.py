import psycopg2
from psycopg2 import sql

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval

ARCHIVE_DIR = "archive"
ERROR_DIR = "error"
GET_DIRECTION = "get"
PUT_DIRECTION = "put"
DIRECTIONS = [(GET_DIRECTION, "Get Files"), (PUT_DIRECTION, "Put Files")]


class FtpUtility(models.AbstractModel):
    _name = "xx.ftp.utility"
    _description = "FTP Utility Object"

    __logger_context = {}

    @staticmethod
    def str2tuple(text):
        return safe_eval("tuple({})".format(text or ""))

    def get_logger(self):
        if not self.__logger_context.get("db_logger"):
            from odoo.addons.dyn_log.models.db_handler import DBLogger

            self.__logger_context.update(
                {"db_logger": DBLogger(self.env.cr, self._name, 0, self.env.uid)}
            )
        return self.__logger_context.get("db_logger")

    def _commit(self):
        if not config["test_enable"]:
            self.env.cr.commit()  # pylint: disable=E8102

    def _rollback(self):
        if not config["test_enable"]:
            self.env.cr.rollback()

    def _handle_callback_exception(self):
        """Method called when an exception is raised.
        Simply logs the exception and rollback the transaction.
        """
        self._rollback()
        self.get_logger().exception(
            f"Call of self.pool.get('{self.model_name}')."
            f"{self.method_name}(cr, uid, *{self.args}) failed for {self}"
        )

    def _callback(self):
        """Run the method associated to the directory
        It takes care of logging and exception handling.
        """
        try:
            args = self.str2tuple(self.args)
            if self.model_name:
                try:
                    model = self.env[self.model_name]
                except Exception:
                    self.get_logger().warning("Model `%s` does not exist." % self.model_name)
                    return False
                if hasattr(model, self.method_name):
                    getattr(model, self.method_name)(*args)
                else:
                    self.get_logger().warning(
                        f"Method `{self.model_name}.{self.method_name}` does not exist."
                    )
                    return False
            return True
        except Exception:
            self._handle_callback_exception()
            return False

    def _try_lock(self):
        """Try to grab a dummy exclusive write-lock to the rows with the given ids,
        to make sure a following write() or unlink() will not block due
        to a process currently executing the tasks"""
        try:
            name = self.display_name
            self._get_lock()
        except psycopg2.errors.LockNotAvailable as e:
            # early rollback to allow translations to work for the user feedback
            self._rollback()
            raise ValidationError(
                _(
                    "The object '{name}' ({id}) is currently "
                    "being executed and may not be modified, "
                    "please try again in a few minutes"
                ).format(name=name, id=self.id)
            ) from e

    def _get_lock(self):
        self.env.cr.execute(
            sql.SQL("SELECT id FROM {} WHERE id = %s FOR UPDATE NOWAIT").format(
                sql.Identifier(self._table)
            ),
            (self.id,),
        )

    def write(self, values):
        for record in self:
            record._try_lock()
        return super().write(values)

    def unlink(self):
        for record in self:
            record._try_lock()
        return super().unlink()
