# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class Log(models.Model):
    _name = "xx.log"
    _description = "Logs"
    _rec_name = "message"
    _access = False

    _order = "date desc, id desc"

    def init(self):
        super().init()
        self._cr.execute("select relname from pg_class where relname in ('xx_log_seq')")
        res = self._cr.fetchone()
        if not res:
            self._cr.execute("create sequence xx_log_seq")
        return True

    @api.depends("uid")
    def _compute_user_name(self):
        user_obj = self.env["res.users"]
        user_id_to_name = {}
        for log in self:
            if log.uid not in user_id_to_name:
                user = user_obj.browse(log.uid)
                if user:
                    name = user.name
                    user_id_to_name[log.uid] = f"{name} [{log.uid}]"
                else:
                    user_id_to_name[log.uid] = f"[{log.uid}]"
            log.user_name = user_id_to_name[log.uid]

    @api.depends("res_id")
    def _compute_res_name(self):
        res_to_name = {}
        for log in self:
            res_key = (log.model_name, log.res_id)
            res_name = f"{res_key[0]},{res_key[1]}"
            if log.model_name and log.res_id:
                if res_key in res_to_name:
                    res_name = res_to_name[res_key]
                else:
                    res = self.env[log.model_name].browse(log.res_id)
                    res_name = res.display_name
            log.res_name = res_name

    date = fields.Datetime(readonly=True)
    uid = fields.Integer(string="User Id", readonly=True)
    user_name = fields.Char(string="User", compute=_compute_user_name)
    model_name = fields.Char(readonly=True)
    res_id = fields.Integer(string="Resource Id", readonly=True, group_operator="count")
    res_name = fields.Char(string="Resource Name", compute=_compute_res_name)
    pid = fields.Integer(string="PID", readonly=True, index=True, group_operator="count")
    level = fields.Char(readonly=True)
    message = fields.Text(readonly=True)

    def scheduled_cleanup(self):
        self.env.cr.execute(
            """
        DELETE
          FROM xx_log
         WHERE date < %s
        """,
            [(datetime.today().date() - relativedelta(months=+1)).strftime("%Y-%m-%d")],
        )
