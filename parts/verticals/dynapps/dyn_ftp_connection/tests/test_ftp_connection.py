from ftplib import error_perm
from unittest.mock import ANY, Mock, call, patch

from odoo.exceptions import ValidationError
from odoo.tests import Form, common
from odoo.tools import config

from ..models.ftp_connection import (
    FTP_DEFAULTS,
    FTP_PROTOCOL,
    RSA_ENCRYPTION,
    SFTP_DEFAULTS,
    SFTP_PROTOCOL,
)


class TestFtpConnection(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ftp_obj = cls.env["xx.ftp.connection"]
        with Form(cls.ftp_obj) as f:
            f.name = "Test FTP Connection User/Password"
            f.ftp_protocol = FTP_PROTOCOL
            f.use_config_file = False
            f.ftp_host = "localhost"
            f.ftp_user = "user"
            f.ftp_password = "password"
        cls.ftp_connection = f.save()
        with Form(cls.ftp_obj) as f:
            f.name = "Test FTP Connection User/Password (Config)"
            f.ftp_protocol = FTP_PROTOCOL
            f.use_config_file = True
            f.config_file_prefix = "test"
        cls.ftp_connection_config = f.save()
        with Form(cls.ftp_obj) as f:
            f.name = "Test SFTP Connection User/Password"
            f.ftp_protocol = SFTP_PROTOCOL
            f.use_config_file = False
            f.ftp_host = "localhost"
            f.ftp_user = "user"
            f.ftp_password = "password"
        cls.sftp_connection = f.save()
        with Form(cls.ftp_obj) as f:
            f.name = "Test SFTP Connection Private Key"
            f.ftp_protocol = SFTP_PROTOCOL
            f.use_config_file = False
            f.authentication = "key"
            f.ftp_host = "localhost"
            f.ftp_user = "user"
            f.private_key = "private_key"
        cls.sftp_connection_pk = f.save()
        with Form(cls.ftp_obj) as f:
            f.name = "Test SFTP Connection Private Key (Config)"
            f.ftp_protocol = SFTP_PROTOCOL
            f.use_config_file = True
            f.authentication = "key"
            f.config_file_prefix = "test"
        cls.sftp_connection_pk_config = f.save()

    def _update_ftp_connection(self, data):
        with Form(self.ftp_obj) as f:
            for field, value in data.items():
                setattr(f, field, value)
        return f.save()

    def test_ftp_connection_defaults(self):
        with Form(self.ftp_obj) as f:
            f.name = "Test FTP Connection"
            f.use_config_file = False
            f.ftp_host = "localhost"
            f.ftp_user = "user"
            f.ftp_password = "password"
            f.ftp_protocol = FTP_PROTOCOL
            for default in FTP_DEFAULTS:
                self.assertEqual(getattr(f, default), FTP_DEFAULTS[default])

    def test_sftp_connection_defaults(self):
        with Form(self.ftp_obj) as f:
            f.name = "Test FTP Connection"
            f.use_config_file = False
            f.ftp_host = "localhost"
            f.ftp_user = "user"
            f.ftp_password = "password"
            f.ftp_protocol = SFTP_PROTOCOL
            for default in FTP_DEFAULTS:
                self.assertEqual(getattr(f, default), SFTP_DEFAULTS[default])

    def test_create_ftp_connection(self):
        data = {"name": "Test FTP Connection", "use_config_file": False}
        with self.assertRaisesRegex(AssertionError, "ftp_host is a required field"):
            self._update_ftp_connection(data)
        with self.assertRaisesRegex(AssertionError, "ftp_user is a required field"):
            data.update({"ftp_host": "localhost"})
            self._update_ftp_connection(data)
        with self.assertRaisesRegex(AssertionError, "ftp_password is a required field"):
            data.update({"ftp_user": "user"})
            self._update_ftp_connection(data)
        data.update({"ftp_password": "password"})
        self._update_ftp_connection(data)

    def test_create_ftp_connection_config(self):
        data = {"name": "Test FTP Connection", "use_config_file": True}
        with self.assertRaisesRegex(AssertionError, "config_file_prefix is a required field"):
            self._update_ftp_connection(data)

    def test_create_sftp_connection(self):
        data = {
            "name": "Test SFTP Connection",
            "ftp_protocol": SFTP_PROTOCOL,
            "use_config_file": False,
        }
        with self.assertRaisesRegex(AssertionError, "ftp_host is a required field"):
            self._update_ftp_connection(data)
        with self.assertRaisesRegex(AssertionError, "ftp_user is a required field"):
            data.update({"ftp_host": "localhost"})
            self._update_ftp_connection(data)
        with self.assertRaisesRegex(AssertionError, "ftp_password is a required field"):
            data.update({"ftp_user": "user"})
            self._update_ftp_connection(data)
        data.update({"ftp_password": "password"})
        self._update_ftp_connection(data)

    def test_create_sftp_connection_pk(self):
        data = {
            "name": "Test SFTP Connection",
            "ftp_protocol": SFTP_PROTOCOL,
            "authentication": "key",
            "use_config_file": False,
        }

        with self.assertRaisesRegex(AssertionError, "ftp_host is a required field"):
            self._update_ftp_connection(data)
        with self.assertRaisesRegex(AssertionError, "ftp_user is a required field"):
            data.update({"ftp_host": "localhost"})
            self._update_ftp_connection(data)
        with self.assertRaisesRegex(AssertionError, "private_key is a required field"):
            data.update({"ftp_user": "user"})
            self._update_ftp_connection(data)
        data.update({"private_key": "private_key"})
        self._update_ftp_connection(data)

    def test_create_sftp_connection_pk_config(self):
        data = {
            "name": "Test SFTP Connection",
            "ftp_protocol": SFTP_PROTOCOL,
            "authentication": "key",
            "use_config_file": True,
        }
        with self.assertRaisesRegex(AssertionError, "config_file_prefix is a required field"):
            self._update_ftp_connection(data)

    def test_ftp_connection(self):
        with patch("ftplib.FTP", autospec=True) as mock_ftp:
            self.ftp_connection.test_connection()
            self.assertEqual(self.ftp_connection.state, "confirm")
            mock_ftp.assert_has_calls(
                [
                    call().connect("localhost", 21, 10),
                    call().login("user", "password"),
                    call().cwd("/"),
                    call().close(),
                ]
            )
        with self.assertRaisesRegex(AssertionError, "can't write on readonly field 'name'"):
            with Form(self.ftp_connection) as f:
                f.name = "Try to update a confirmed connection"
        self.ftp_connection.to_draft()
        self.assertEqual(self.ftp_connection.state, "draft")
        with Form(self.ftp_connection) as f:
            f.name = "Try to update a confirmed connection"

    def test_ftp_connection_tls(self):
        with patch("ftplib.FTP_TLS", autospec=True) as mock_ftp:
            self.ftp_connection.ftp_tls = True
            self.ftp_connection.test_connection()
            self.assertEqual(self.ftp_connection.state, "confirm")
            mock_ftp.assert_has_calls(
                [
                    call().connect("localhost", 21, 10),
                    call().login("user", "password"),
                    call().cwd("/"),
                    call().close(),
                ]
            )

    def test_ftp_connection_config(self):
        with patch("ftplib.FTP", autospec=True):
            with self.assertRaisesRegex(
                ValidationError, "Define 'test_ftp_host' in the configuration file!"
            ):
                self.ftp_connection_config.test_connection()
        with patch("ftplib.FTP", autospec=True), patch.object(
            config, "options", {**config.options, "test_ftp_host": "localhost"}
        ):
            with self.assertRaisesRegex(
                ValidationError, "Define 'test_ftp_port' in the configuration file!"
            ):
                self.ftp_connection_config.test_connection()
        with patch("ftplib.FTP", autospec=True), patch.object(
            config, "options", {**config.options, "test_ftp_host": "localhost", "test_ftp_port": 21}
        ):
            with self.assertRaisesRegex(
                ValidationError, "Define 'test_ftp_user' in the configuration file!"
            ):
                self.ftp_connection_config.test_connection()
        with patch("ftplib.FTP", autospec=True), patch.object(
            config,
            "options",
            {
                **config.options,
                "test_ftp_host": "localhost",
                "test_ftp_port": 21,
                "test_ftp_user": "user",
            },
        ):
            with self.assertRaisesRegex(
                ValidationError, "Define 'test_ftp_password' in the configuration file!"
            ):
                self.ftp_connection_config.test_connection()

        with patch("ftplib.FTP", autospec=True) as mock_ftp, patch.object(
            config,
            "options",
            {
                **config.options,
                "test_ftp_host": "localhost",
                "test_ftp_port": 21,
                "test_ftp_user": "user",
                "test_ftp_password": "password",
            },
        ):
            self.ftp_connection_config.test_connection()
            self.assertEqual(self.ftp_connection_config.state, "confirm")
            mock_ftp.assert_has_calls(
                [
                    call().connect("localhost", 21, 10),
                    call().login("user", "password"),
                    call().cwd("/"),
                    call().close(),
                ]
            )

    @patch("ftplib.FTP")
    def test_ftp_connection_failed(self, mock_ftp_class):
        mock_ftp_instance = mock_ftp_class.return_value
        mock_ftp_instance.login.side_effect = error_perm("530 Login authentication failed")
        with self.assertRaisesRegex(
            ValidationError, "Connection Failed: '530 Login authentication failed'"
        ):
            self.ftp_connection.test_connection()

    @patch("ftplib.FTP")
    def test_ftp_connection_invalid_base_directory(self, mock_ftp_class):
        mock_ftp_instance = mock_ftp_class.return_value
        mock_ftp_instance.cwd.side_effect = error_perm("550 Not Found")
        with self.assertRaisesRegex(ValidationError, "Check directory 'invalid' on the ftp server"):
            self.ftp_connection.ftp_base = "invalid"
            self.ftp_connection.test_connection()

    def test_ftp_connection_base_directory(self):
        with patch("ftplib.FTP", autospec=True) as mock_ftp:
            self.ftp_connection.ftp_base = "home"
            self.ftp_connection.test_connection()
            mock_ftp.assert_has_calls(
                [
                    call().connect("localhost", 21, 10),
                    call().login("user", "password"),
                    call().cwd("home"),
                    call().close(),
                ]
            )

    def test_ftp_connection_list_dir(self):
        with patch("ftplib.FTP", autospec=True) as mock_ftp:
            self.ftp_connection.list_dir(self.ftp_connection.get_connection(), "/home")
            mock_ftp.assert_has_calls(
                [
                    call().connect("localhost", 21, 10),
                    call().login("user", "password"),
                    call().nlst("/home"),
                ]
            )

    def test_ftp_connection_get(self):
        with patch("ftplib.FTP", autospec=True) as mock_ftp:
            self.ftp_connection.get_file(
                self.ftp_connection.get_connection(), "test.txt", "/tmp/test.txt"
            )
            mock_ftp.assert_has_calls(
                [
                    call().connect("localhost", 21, 10),
                    call().login("user", "password"),
                    call().retrbinary("RETR " + "test.txt", ANY),
                ]
            )

    def test_ftp_connection_put(self):
        with patch("ftplib.FTP", autospec=True) as mock_ftp:
            self.ftp_connection.put_file(
                self.ftp_connection.get_connection(), "/tmp/test.txt", "test.txt"
            )
            mock_ftp.assert_has_calls(
                [
                    call().connect("localhost", 21, 10),
                    call().login("user", "password"),
                    call().storbinary("STOR " + "test.txt", ANY),
                ]
            )

    def test_sftp_connection(self):
        with patch("paramiko.Transport", autospec=True) as mock_sftp:
            self.sftp_connection.test_connection()
            mock_sftp.assert_has_calls(
                [
                    call().connect(username="user", password="password"),
                    call().open_sftp_client(),
                    call().open_sftp_client().chdir("/"),
                    call().open_sftp_client().close(),
                ]
            )

    def test_sftp_connection_base_directory(self):
        with patch("paramiko.Transport", autospec=True) as mock_sftp:
            self.sftp_connection.ftp_base = "home"
            self.sftp_connection.test_connection()
            mock_sftp.assert_has_calls(
                [
                    call().connect(username="user", password="password"),
                    call().open_sftp_client(),
                    call().open_sftp_client().chdir("home"),
                    call().open_sftp_client().close(),
                ]
            )

    def test_sftp_connection_list_dir(self):
        with patch("paramiko.Transport", autospec=True) as mock_sftp:
            self.sftp_connection.list_dir(self.sftp_connection.get_connection(), "/home")
            mock_sftp.assert_has_calls(
                [
                    call().connect(username="user", password="password"),
                    call().open_sftp_client(),
                    call().open_sftp_client().listdir("/home"),
                ]
            )

    def test_sftp_connection_get(self):
        with patch("paramiko.Transport", autospec=True) as mock_sftp:
            self.sftp_connection.get_file(
                self.sftp_connection.get_connection(), "test.txt", "/tmp/test.txt"
            )
            mock_sftp.assert_has_calls(
                [
                    call().connect(username="user", password="password"),
                    call().open_sftp_client(),
                    call().open_sftp_client().get("test.txt", "/tmp/test.txt"),
                ]
            )

    def test_sftp_connection_put(self):
        with patch("paramiko.Transport", autospec=True) as mock_sftp:
            self.sftp_connection.put_file(
                self.sftp_connection.get_connection(),
                "/tmp/test.txt",
                "test.txt",
            )
            mock_sftp.assert_has_calls(
                [
                    call().connect(username="user", password="password"),
                    call().open_sftp_client(),
                    call().open_sftp_client().put("/tmp/test.txt", "test.txt", confirm=False),
                ]
            )

    def test_sftp_connection_pk(self):
        with patch("paramiko.Transport", autospec=True) as mock_sftp, patch(
            "paramiko.Ed25519Key.from_private_key_file"
        ) as mock_private_key_file:
            self.sftp_connection_pk.test_connection()
            mock_private_key_file.assert_called_once_with("private_key", False)
            mock_sftp.assert_has_calls(
                [
                    call().start_client(),
                    call().auth_publickey("user", ANY),
                    call().open_session(),
                    call().open_sftp_client(),
                    call().open_sftp_client().chdir("/"),
                    call().open_sftp_client().close(),
                ]
            )

    def test_sftp_connection_pk_rsa(self):
        with patch("paramiko.Transport", autospec=True) as mock_sftp, patch(
            "paramiko.RSAKey.from_private_key_file"
        ) as mock_private_key_file:
            self.sftp_connection_pk.cryptography_algorithm = RSA_ENCRYPTION
            self.sftp_connection_pk.test_connection()
            mock_private_key_file.assert_called_once_with("private_key", False)
            mock_sftp.assert_has_calls(
                [
                    call().start_client(),
                    call().auth_publickey("user", ANY),
                    call().open_session(),
                    call().open_sftp_client(),
                    call().open_sftp_client().chdir("/"),
                    call().open_sftp_client().close(),
                ]
            )

    def test_sftp_connection_pk_config(self):
        with patch("paramiko.Transport", autospec=True), patch.object(
            config,
            "options",
            {
                **config.options,
                "test_ftp_host": "localhost",
                "test_ftp_port": 21,
                "test_ftp_user": "user",
            },
        ):
            with self.assertRaisesRegex(
                ValidationError, "Define 'test_private_key' in the configuration file!"
            ):
                self.sftp_connection_pk_config.test_connection()
        with patch("paramiko.Transport", autospec=True), patch.object(
            config,
            "options",
            {
                **config.options,
                "test_ftp_host": "localhost",
                "test_ftp_port": 21,
                "test_ftp_user": "user",
                "test_private_key": "private_key",
            },
        ):
            with self.assertRaisesRegex(
                ValidationError, "Define 'test_passphrase' in the configuration file!"
            ):
                self.sftp_connection_pk_config.test_connection()
        with patch("paramiko.Transport", autospec=True) as mock_sftp, patch(
            "paramiko.Ed25519Key.from_private_key_file"
        ) as mock_private_key_file, patch.object(
            config,
            "options",
            {
                **config.options,
                "test_ftp_host": "localhost",
                "test_ftp_port": 21,
                "test_ftp_user": "user",
                "test_private_key": "private_key",
                "test_passphrase": "passphrase",
            },
        ):
            self.sftp_connection_pk_config.test_connection()
            mock_private_key_file.assert_called_once_with("private_key", "passphrase")
            mock_sftp.assert_has_calls(
                [
                    call().start_client(),
                    call().auth_publickey("user", ANY),
                    call().open_session(),
                    call().open_sftp_client(),
                    call().open_sftp_client().chdir("/"),
                    call().open_sftp_client().close(),
                ]
            )


class TestInvalidProtocol(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ftp_obj = cls.env["xx.ftp.connection"]
        with Form(cls.ftp_obj) as f:
            f.name = "Test FTP Connection User/Password"
            f.ftp_protocol = FTP_PROTOCOL
            f.use_config_file = False
            f.ftp_host = "localhost"
            f.ftp_user = "user"
            f.ftp_password = "password"
        cls.ftp_connection = f.save()
        cls.cr.execute(
            "UPDATE xx_ftp_connection SET ftp_protocol = 'invalid' WHERE id = %s",
            [cls.ftp_connection.id],
        )
        with Form(cls.ftp_obj) as f:
            f.name = "Test SFTP Connection User/Password"
            f.ftp_protocol = SFTP_PROTOCOL
            f.use_config_file = False
            f.ftp_host = "localhost"
            f.ftp_user = "user"
            f.ftp_password = "password"
        cls.sftp_connection = f.save()
        cls.cr.execute(
            "UPDATE xx_ftp_connection SET authentication = 'invalid' WHERE id = %s",
            [cls.sftp_connection.id],
        )

    def test_get_ftp_connection(self):
        with self.assertRaisesRegex(
            ValidationError, "get_ftp_connection not implemented for 'invalid'"
        ):
            self.ftp_connection.get_connection()

    def test_get_sftp_connection(self):
        with self.assertRaisesRegex(
            ValidationError, "get_sftp_connection not implemented for 'invalid'"
        ):
            with patch("paramiko.Transport", autospec=True):
                self.sftp_connection.get_sftp_connection()

    def test_change_ftp_directory(self):
        with self.assertRaisesRegex(
            ValidationError, "change_ftp_directory not implemented for 'invalid'"
        ):
            ftp_connection = Mock()
            self.ftp_connection.change_ftp_directory(ftp_connection, "/home")

    def test_list_dir(self):
        with self.assertRaisesRegex(ValidationError, "list_dir not implemented for 'invalid'"):
            ftp_connection = Mock()
            self.ftp_connection.list_dir(ftp_connection, "/home")

    def test_get_file(self):
        with self.assertRaisesRegex(ValidationError, "get_file not implemented for 'invalid'"):
            ftp_connection = Mock()
            self.ftp_connection.get_file(ftp_connection, "test.txt", "/tmp/test.txt")

    def test_put_file(self):
        with self.assertRaisesRegex(ValidationError, "put_file not implemented for 'invalid'"):
            ftp_connection = Mock()
            self.ftp_connection.put_file(ftp_connection, "/tmp/test.txt", "test.txt")


class TestInvalidCryptographyAlgorithm(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ftp_obj = cls.env["xx.ftp.connection"]
        with Form(cls.ftp_obj) as f:
            f.name = "Test SFTP Connection Private Key"
            f.ftp_protocol = SFTP_PROTOCOL
            f.use_config_file = False
            f.ftp_host = "localhost"
            f.ftp_user = "user"
            f.authentication = "key"
            f.private_key = "private_key"
        cls.sftp_connection = f.save()
        cls.cr.execute(
            "UPDATE xx_ftp_connection SET cryptography_algorithm = 'invalid' WHERE id = %s",
            [cls.sftp_connection.id],
        )

    def test_get_sftp_connection(self):
        with self.assertRaisesRegex(
            ValidationError,
            "get_sftp_connection not implemented for cryptography algorithm 'invalid'",
        ):
            with patch("paramiko.Transport", autospec=True):
                self.sftp_connection.get_sftp_connection()
