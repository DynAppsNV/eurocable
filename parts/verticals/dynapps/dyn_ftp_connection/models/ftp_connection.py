import ftplib
import logging
import threading
import traceback

import paramiko

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.config import config

_logger = logging.getLogger(__name__)

FTP_PROTOCOL = "ftp"
SFTP_PROTOCOL = "sftp"
PROTOCOLS = [(FTP_PROTOCOL, "FTP"), (SFTP_PROTOCOL, "SFTP")]
FTP_DEFAULTS = {"ftp_port": 21, "ftp_timeout": 10}
SFTP_DEFAULTS = {"ftp_port": 22, "ftp_passive": False, "ftp_timeout": 0}

USER_AUTHENTICATION = "user"
KEY_AUTHENTICATION = "key"
USER_KEY_AUTHENTICATION = "user_key"
AUTHENTICATIONS = [
    (USER_AUTHENTICATION, "User/Password"),
    (KEY_AUTHENTICATION, "Private Key"),
    (USER_KEY_AUTHENTICATION, "User/Key"),
]
RSA_ENCRYPTION = "rsa"
ED25519_ENCRYPTION = "ed25519"
CRYPTOGRAPHY_ALGORITHMS = [
    (RSA_ENCRYPTION, "RSA"),
    (ED25519_ENCRYPTION, "Ed25519"),
]
USER_AUTHENTICATION_DEFAULTS = {
    "cryptography_algorithm": False,
    "private_key": False,
    "passphrase": False,
}
KEY_AUTHENTICATION_DEFAULTS = {"ftp_password": False, "cryptography_algorithm": "ed25519"}
CONFIG_FILE_DEFAULTS = {
    "ftp_host": False,
    "ftp_port": False,
    "ftp_user": False,
    "ftp_password": False,
    "private_key": False,
    "passphrase": False,
}
NO_CONFIG_FILE_DEFAULTS = {"config_file_prefix": False}
STATES = [("draft", "Draft"), ("confirm", "Confirmed")]


class FtpConnection(models.Model):
    _name = "xx.ftp.connection"
    _description = "FTP Connection"

    name = fields.Char(
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
    )
    use_config_file = fields.Boolean(
        string="Use Config File?",
        default=True,
    )
    config_file_prefix = fields.Char()
    ftp_protocol = fields.Selection(
        selection=PROTOCOLS,
        string="FTP Protocol",
        default="ftp",
    )
    ftp_host = fields.Char(
        string="Host",
    )
    ftp_port = fields.Integer(
        string="Port",
    )
    ftp_base = fields.Char(
        string="Base",
        required=True,
        default="/",
    )
    ftp_passive = fields.Boolean(
        string="Passive Mode?",
        default=False,
    )
    ftp_tls = fields.Boolean(
        string="Enable TLS",
        default=False,
    )
    ftp_timeout = fields.Integer(
        string="Timeout",
        default=10,
    )
    authentication = fields.Selection(
        selection=AUTHENTICATIONS,
        default="user",
    )
    cryptography_algorithm = fields.Selection(
        selection=CRYPTOGRAPHY_ALGORITHMS,
    )
    ftp_user = fields.Char(
        string="User",
    )
    ftp_password = fields.Char(
        string="Password",
    )
    private_key = fields.Char()
    passphrase = fields.Char()
    state = fields.Selection(selection=STATES, default="draft")
    active = fields.Boolean(
        string="Active?",
        default=True,
    )

    @api.onchange("ftp_protocol")
    def onchange_ftp_protocol(self):
        if self.ftp_protocol == FTP_PROTOCOL:
            self.update(FTP_DEFAULTS)
        elif self.ftp_protocol == SFTP_PROTOCOL:
            self.update(SFTP_DEFAULTS)

    @api.onchange("authentication")
    def onchange_authentication(self):
        if self.authentication == USER_AUTHENTICATION:
            self.update(USER_AUTHENTICATION_DEFAULTS)
        elif self.authentication == KEY_AUTHENTICATION:
            self.update(KEY_AUTHENTICATION_DEFAULTS)

    @api.onchange("use_config_file")
    def onchange_use_config_file(self):
        if self.use_config_file:
            self.update(CONFIG_FILE_DEFAULTS)
        else:
            self.update(NO_CONFIG_FILE_DEFAULTS)
            self.onchange_ftp_protocol()

    def _close_ftp_connection(self, ftp_connection):
        ftp_connection.close()
        # FTP Client uses transport, this needs to be closed
        # because otherwise the thread never stops
        transport = ftp_connection.sock.transport
        if transport:
            transport.close()

    def _test_connection_hook(self, ftp_connection):
        pass

    def _test_connection(self):
        self.ensure_one()
        try:
            ftp_connection = self.get_connection()
        except Exception as e:
            err_msg = _("Connection Failed: '{}'").format(format(str(e)))
            raise ValidationError(err_msg) from e
        if self.ftp_base:
            self.check_ftp_directory(ftp_connection, self.ftp_base)
        self._test_connection_hook(ftp_connection)
        self._close_ftp_connection(ftp_connection)
        return True

    def test_connection(self):
        self._test_connection()
        return self.write({"state": "confirm"})

    def check_ftp_directory(self, ftp_connection, ftp_directory):
        try:
            self.change_ftp_directory(ftp_connection, ftp_directory)
        except Exception as e:
            err_msg = _("Check directory '{directory}' on the ftp server\n{traceback}").format(
                directory=ftp_directory, traceback=traceback.format_exc()
            )
            raise ValidationError(err_msg) from e

    def get_config_file_entry(self, entry):
        config_entry = self.config_file_prefix + "_" + entry
        value = config.get(config_entry)
        if value is None:
            err_msg = _("Define '{}' in the configuration file!").format(config_entry)
            raise ValidationError(err_msg)
        return value

    def get_ftp_host(self):
        if self.use_config_file:
            return self.get_config_file_entry("ftp_host")
        else:
            return self.ftp_host

    def get_ftp_port(self):
        if self.use_config_file:
            return int(self.get_config_file_entry("ftp_port"))
        else:
            return self.ftp_port

    def get_ftp_user(self):
        if self.use_config_file:
            return self.get_config_file_entry("ftp_user")
        else:
            return self.ftp_user

    def get_ftp_password(self):
        if self.use_config_file:
            return self.get_config_file_entry("ftp_password")
        else:
            return self.ftp_password

    def get_private_key(self):
        if self.use_config_file:
            return self.get_config_file_entry("private_key")
        else:
            return self.private_key

    def get_passphrase(self):
        if self.use_config_file:
            return self.get_config_file_entry("passphrase")
        else:
            return self.passphrase

    def get_ftp_connection(self):
        if self.ftp_tls:
            ftp = ftplib.FTP_TLS()
        else:
            ftp = ftplib.FTP(timeout=self.ftp_timeout)
        ftp.set_pasv(self.ftp_passive)
        ftp.connect(self.get_ftp_host(), self.get_ftp_port(), self.ftp_timeout)
        ftp.login(self.get_ftp_user(), self.get_ftp_password())
        return ftp

    def get_sftp_connection(self):
        """
        USER_KEY_AUTHENTICATION is fix for Bug in paramiko with double authentication.
        Initial auth_handler authentication is reset when authenticating the second time.
        Fix is from https://github.com/paramiko/paramiko/issues/519
        """
        if self.authentication == USER_KEY_AUTHENTICATION:
            transport = paramiko.Transport(
                (self.get_ftp_host(), self.get_ftp_port()),
                disabled_algorithms={"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]},
            )
        else:
            transport = paramiko.Transport((self.get_ftp_host(), self.get_ftp_port()))
        if self.authentication == USER_AUTHENTICATION:
            transport.connect(
                username=self.get_ftp_user(),
                password=self.get_ftp_password(),
            )
        elif self.authentication == KEY_AUTHENTICATION:
            if self.cryptography_algorithm == RSA_ENCRYPTION:
                private_key = paramiko.RSAKey.from_private_key_file(
                    self.get_private_key(), self.get_passphrase()
                )
            elif self.cryptography_algorithm == ED25519_ENCRYPTION:
                private_key = paramiko.Ed25519Key.from_private_key_file(
                    self.get_private_key(), self.get_passphrase()
                )
            else:
                err_msg = _(
                    "get_sftp_connection not implemented for cryptography algorithm '{}'"
                ).format(self.cryptography_algorithm)
                raise ValidationError(err_msg)
            transport.start_client()
            transport.auth_publickey(self.get_ftp_user(), private_key)
            transport.open_session()
        elif self.authentication == USER_KEY_AUTHENTICATION:
            private_key = paramiko.RSAKey.from_private_key_file(self.get_private_key())
            transport.connect()
            transport.auth_publickey(self.get_ftp_user(), private_key)
            event = threading.Event()

            auth_handler = paramiko.auth_handler.AuthHandler(transport)
            transport.auth_handler = auth_handler
            transport.lock.acquire()

            auth_handler.auth_event = event
            auth_handler.auth_method = "password"

            auth_handler.username = self.get_ftp_user()
            auth_handler.password = self.get_ftp_password()

            message = paramiko.Message().add_string("ssh-userauth")
            message.rewind()
            auth_handler._parse_service_accept(message)
            transport.lock.release()

            auth_handler.wait_for_response(event)
        else:
            err_msg = _("get_sftp_connection not implemented for '{}'").format(self.authentication)
            raise ValidationError(err_msg)
        return transport.open_sftp_client()

    def get_connection(self):
        if self.ftp_protocol == FTP_PROTOCOL:
            return self.get_ftp_connection()
        elif self.ftp_protocol == SFTP_PROTOCOL:
            return self.get_sftp_connection()
        else:
            err_msg = _("get_ftp_connection not implemented for '{}'").format(self.ftp_protocol)
            raise ValidationError(err_msg)

    def change_ftp_directory(self, ftp_connection, ftp_directory):
        if self.ftp_protocol == FTP_PROTOCOL:
            ftp_connection.cwd(ftp_directory)
        elif self.ftp_protocol == SFTP_PROTOCOL:
            ftp_connection.chdir(ftp_directory)
        else:
            err_msg = _("change_ftp_directory not implemented for '{}'").format(self.ftp_protocol)
            raise ValidationError(err_msg)

    def list_dir(self, ftp_connection, ftp_directory):
        if self.ftp_protocol == FTP_PROTOCOL:
            return ftp_connection.nlst(ftp_directory)
        elif self.ftp_protocol == SFTP_PROTOCOL:
            return ftp_connection.listdir(ftp_directory)
        else:
            err_msg = _("list_dir not implemented for '{}'").format(self.ftp_protocol)
            raise ValidationError(err_msg)

    def get_file(self, ftp_connection, remote_file, local_file):
        if self.ftp_protocol == FTP_PROTOCOL:
            with open(local_file, "wb") as f:
                ftp_connection.retrbinary("RETR " + remote_file, f.write)
        elif self.ftp_protocol == SFTP_PROTOCOL:
            ftp_connection.get(remote_file, local_file)
        else:
            err_msg = _("get_file not implemented for '{}'").format(self.ftp_protocol)
            raise ValidationError(err_msg)

    def put_file(self, ftp_connection, local_file, remote_file, confirm_file_size=False):
        if self.ftp_protocol == FTP_PROTOCOL:
            ftp_connection.storbinary("STOR %s" % remote_file, open(local_file, "rb"))
        elif self.ftp_protocol == SFTP_PROTOCOL:
            ftp_connection.put(local_file, remote_file, confirm=confirm_file_size)
        else:
            err_msg = _("put_file not implemented for '{}'").format(self.ftp_protocol)
            raise ValidationError(err_msg)

    def to_draft(self):
        self.ensure_one()
        return self.write({"state": "draft"})
