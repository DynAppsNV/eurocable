from unittest.mock import ANY, call, patch

import psycopg2

from odoo.exceptions import ValidationError
from odoo.tests import Form, common
from odoo.tools import mute_logger

from odoo.addons.dyn_ftp_connection.models.ftp_connection import (
    FTP_PROTOCOL,
    SFTP_PROTOCOL,
    FtpConnection,
)
from odoo.addons.dyn_ftp_transfer.models.ftp_utility import FtpUtility

from ..models.ftp_connection_directory import GET_DIRECTION, PUT_DIRECTION


class TestFtpCommon(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,  # no jobs thanks
            )
        )

    def _create_ftp_connection(self, direction, data_dir_prefix=True):
        with Form(self.ftp_obj) as f:
            f.name = "Test FTP Connection User/Password"
            f.ftp_protocol = FTP_PROTOCOL
            f.use_config_file = False
            f.ftp_host = "localhost"
            f.ftp_user = "user"
            f.ftp_password = "password"
        ftp_connection = f.save()
        if direction == GET_DIRECTION or direction == "both":
            with Form(ftp_connection) as f:
                with f.ftp_directory_ids.new() as d:
                    d.name = "out"
                    d.data_dir_prefix = data_dir_prefix
                    d.direction = GET_DIRECTION
                    d.local_directory = "ftp/in"
                    d.user_id = self.user_admin
        if direction == PUT_DIRECTION or direction == "both":
            with Form(ftp_connection) as f:
                with f.ftp_directory_ids.new() as d:
                    d.name = "in"
                    d.data_dir_prefix = data_dir_prefix
                    d.direction = PUT_DIRECTION
                    d.local_directory = "ftp/out"
                    d.user_id = self.user_admin
        return ftp_connection

    def _create_sftp_connection(self, direction, data_dir_prefix=True):
        with Form(self.ftp_obj) as f:
            f.name = "Test SFTP Connection Private Key"
            f.ftp_protocol = SFTP_PROTOCOL
            f.use_config_file = False
            f.authentication = "key"
            f.ftp_host = "localhost"
            f.ftp_user = "user"
            f.private_key = "private_key"
        sftp_connection = f.save()
        if direction == GET_DIRECTION or direction == "both":
            with Form(sftp_connection) as f:
                with f.ftp_directory_ids.new() as d:
                    d.name = "out"
                    d.data_dir_prefix = data_dir_prefix
                    d.direction = GET_DIRECTION
                    d.local_directory = "ftp/in"
                    d.user_id = self.user_admin
        if direction == PUT_DIRECTION or direction == "both":
            with Form(sftp_connection) as f:
                with f.ftp_directory_ids.new() as d:
                    d.name = "in"
                    d.data_dir_prefix = data_dir_prefix
                    d.direction = PUT_DIRECTION
                    d.local_directory = "ftp/out"
                    d.user_id = self.user_admin
        return sftp_connection

    @staticmethod
    def _add_ftp_directory(ftp_connection, data):
        with ftp_connection.ftp_directory_ids.new() as d:
            for field, value in data.items():
                setattr(d, field, value)
        return d.save()


class TestFtpConnectionLocked(TestFtpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ftp_obj = cls.env["xx.ftp.connection"]
        cls.ftp_file_handler_obj = cls.env["xx.ftp.file.handler"]
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.ftp_connection = cls._create_ftp_connection(cls, direction=GET_DIRECTION)
        with patch(
            "ftplib.FTP",
            **{
                "return_value.nlst.return_value": ["foo"],
            },
        ):
            cls.ftp_connection.test_connection()

    @patch(
        "ftplib.FTP",
        **{
            "return_value.nlst.return_value": ["foo"],
        },
    )
    def test_process_ftp_connections_locked_dir(self, _mock_ftp):
        with patch.object(FtpUtility, "_get_lock", side_effect=psycopg2.errors.LockNotAvailable):
            with self.assertRaisesRegex(
                ValidationError, " is currently being executed and may not be modified"
            ):
                self.ftp_connection.process_ftp_connections()


class TestFtpConnection(TestFtpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ftp_obj = cls.env["xx.ftp.connection"]
        cls.ftp_file_handler_obj = cls.env["xx.ftp.file.handler"]
        cls.user_admin = cls.env.ref("base.user_admin")

    @mute_logger("xx_log")
    def test_ftp_connection(self):
        with patch("ftplib.FTP", autospec=True):
            ftp_connection = self._create_ftp_connection("none")
            ftp_connection.ftp_directory_ids.unlink()
            with self.assertRaisesRegex(ValidationError, "Please define some directories!"):
                ftp_connection.test_connection()

    @mute_logger("xx_log")
    def test_check_directories_get(self):
        with patch("ftplib.FTP", autospec=True) as mock_ftp:
            ftp_connection = self._create_ftp_connection(GET_DIRECTION)
            ftp_connection.test_connection()
            mock_ftp.assert_has_calls(
                [
                    call().connect("localhost", 21, 10),
                    call().login("user", "password"),
                    call().cwd("/"),
                    call().cwd("/out"),
                    call().close(),
                ]
            )

    @mute_logger("xx_log")
    def test_check_directories_put(self):
        with patch("ftplib.FTP", autospec=True) as mock_ftp:
            ftp_connection = self._create_ftp_connection(PUT_DIRECTION)
            ftp_connection.test_connection()
            mock_ftp.assert_has_calls(
                [
                    call().connect("localhost", 21, 10),
                    call().login("user", "password"),
                    call().cwd("/"),
                    call().cwd("/in"),
                    call().close(),
                ]
            )

    @mute_logger("xx_log")
    def test_check_directories(self):
        with patch("ftplib.FTP", autospec=True) as mock_ftp:
            ftp_connection = self._create_ftp_connection("both")
            ftp_connection.test_connection()
            mock_ftp.assert_has_calls(
                [
                    call().connect("localhost", 21, 10),
                    call().login("user", "password"),
                    call().cwd("/"),
                    call().cwd("/out"),
                    call().cwd("/in"),
                    call().close(),
                ]
            )

    @mute_logger("xx_log")
    def test_create_ftp_directory_get(self):
        ftp_connection = self._create_ftp_connection("none")
        with Form(ftp_connection) as f:
            data = {"name": "Test Directory"}
            with self.assertRaisesRegex(AssertionError, "'direction' is a required field"):
                self._add_ftp_directory(f, data)
            data.update({"direction": GET_DIRECTION})
            with self.assertRaisesRegex(AssertionError, "'local_directory' is a required field"):
                self._add_ftp_directory(f, data)
            data.update({"local_directory": "ftp/in"})
            with self.assertRaisesRegex(AssertionError, "'user_id' is a required field"):
                self._add_ftp_directory(f, data)
            data.update({"user_id": self.user_admin})
            self._add_ftp_directory(f, data)

    @mute_logger("xx_log")
    def test_create_ftp_directory_put(self):
        ftp_connection = self._create_ftp_connection("none")
        with Form(ftp_connection) as f:
            data = {"name": "Test Directory"}
            with self.assertRaisesRegex(AssertionError, "'direction' is a required field"):
                self._add_ftp_directory(f, data)
            data.update({"direction": PUT_DIRECTION})
            with self.assertRaisesRegex(AssertionError, "'local_directory' is a required field"):
                self._add_ftp_directory(f, data)
            data.update({"local_directory": "ftp/out"})
            with self.assertRaisesRegex(AssertionError, "'user_id' is a required field"):
                self._add_ftp_directory(f, data)
            data.update({"user_id": self.user_admin})
            self._add_ftp_directory(f, data)

    @mute_logger("xx_log")
    @patch(
        "ftplib.FTP",
        **{
            "return_value.nlst.return_value": ["foo.txt", "foo2.txt"],
            "return_value.size.return_value": 100,
        },
    )
    def test_process_ftp_connection_get(self, _mock_ftp):
        ftp_connection = self._create_ftp_connection(GET_DIRECTION)
        ftp_connection.test_connection()
        ftp_connection.process_ftp_connections()

    @mute_logger("xx_log")
    @patch(
        "ftplib.FTP",
        **{
            "return_value.nlst.return_value": ["foo.txt", "foo2.txt"],
            "return_value.size.return_value": 100,
        },
    )
    def test_process_ftp_connection_get_archive_remote(self, mock_ftp):
        ftp_connection = self._create_ftp_connection(GET_DIRECTION)
        ftp_connection.ftp_directory_ids.filtered(
            lambda d: d.direction == GET_DIRECTION
        ).archive_name = "archive/out/"
        ftp_connection.test_connection()
        ftp_connection.process_ftp_connections()
        mock_ftp.assert_has_calls(
            [
                call().size("out/foo.txt"),
                call().retrbinary("RETR out/foo.txt", ANY),
                call().rename("out/foo.txt", "archive/out/foo.txt"),
            ]
        )
        mock_ftp.assert_has_calls(
            [
                call().size("out/foo2.txt"),
                call().retrbinary("RETR out/foo2.txt", ANY),
                call().rename("out/foo2.txt", "archive/out/foo2.txt"),
            ]
        )

    @mute_logger("xx_log")
    @patch(
        "ftplib.FTP",
        **{
            "return_value.nlst.return_value": ["foo.txt", "foo2.txt"],
            "return_value.size.return_value": 100,
        },
    )
    def test_process_ftp_connection_get_save_attachment(self, _mock_ftp):
        ftp_connection = self._create_ftp_connection(GET_DIRECTION)
        ftp_connection.ftp_directory_ids.filtered(
            lambda d: d.direction == GET_DIRECTION
        ).attach_file = True
        ftp_connection.test_connection()
        ftp_connection.process_ftp_connections()

    @mute_logger("xx_log")
    def test_check_method(self):
        ftp_connection = self._create_ftp_connection(GET_DIRECTION)
        with self.assertRaisesRegex(
            ValidationError, "Method 'test_method' does not exist in model 'res.partner'!"
        ):
            ftp_connection.ftp_directory_ids.filtered(
                lambda d: d.direction == GET_DIRECTION
            ).update(
                {
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "method_name": "test_method",
                }
            )

    @mute_logger("xx_log")
    def test_args(self):
        ftp_connection = self._create_ftp_connection(GET_DIRECTION)
        with self.assertRaisesRegex(ValidationError, "Invalid arguments: 1, 2"):
            ftp_connection.ftp_directory_ids.filtered(
                lambda d: d.direction == GET_DIRECTION
            ).update(
                {
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "method_name": "write",
                    "args": "1, 2",
                }
            )
        ftp_connection.ftp_directory_ids.filtered(lambda d: d.direction == GET_DIRECTION).update(
            {
                "model_id": self.env.ref("base.model_res_partner").id,
                "method_name": "write",
                "args": "(1, 2)",
            }
        )

    @mute_logger("xx_log")
    @patch(
        "ftplib.FTP",
        **{
            "return_value.nlst.return_value": ["foo", "foo2"],
        },
    )
    def test_process_ftp_connection_get_include_subdirs(self, mock_ftp):
        mock_instance = mock_ftp.return_value
        mock_instance.size.side_effect = [Exception("Foo"), Exception("Foo")]
        ftp_connection = self._create_ftp_connection(GET_DIRECTION)
        ftp_connection.ftp_directory_ids.filtered(
            lambda d: d.direction == GET_DIRECTION
        ).include_subdirs = True
        ftp_connection.test_connection()
        ftp_connection.process_ftp_connections()

    @mute_logger("xx_log")
    @patch(
        "ftplib.FTP",
        **{
            "return_value.nlst.return_value": ["partner.json"],
        },
    )
    def test_process_ftp_connection_create_partner(self, mock_ftp):
        # Set up a mock retrbinary method
        def mock_retrbinary(command, callback):
            # Simulate the behavior of retrbinary by calling the callback function with the data
            callback(data_to_download)

        # Define the data to be downloaded
        data_to_download = b"{'name': 'Donald Duck'}"
        # Create a mock FTP instance
        mock_ftp_instance = mock_ftp.return_value
        mock_ftp_instance.retrbinary.side_effect = mock_retrbinary

        ftp_connection = self._create_ftp_connection(GET_DIRECTION)
        ftp_directory = ftp_connection.ftp_directory_ids.filtered(
            lambda d: d.direction == GET_DIRECTION
        )
        ftp_directory.model_id = self.env.ref("base.model_res_partner").id
        ftp_directory.method_name = "create"
        ftp_directory.args = b"[{'name': 'Donald Duck'}]"
        ftp_connection.test_connection()
        ftp_connection.process_ftp_connections()
        file_handler = self.env["xx.ftp.file.handler"].search(
            [("ftp_connection_directory_id", "=", ftp_directory.id)]
        )
        self.assertTrue(file_handler)
        self.assertEqual(file_handler.state, "new")
        with open(file_handler.filename) as file:
            content = file.read()
        self.assertEqual(content, data_to_download.decode("utf-8"))
        self.ftp_file_handler_obj.process_ftp_files()
        self.assertEqual(file_handler.state, "success")
        self.assertIn("ftp/in/archive/partner.json", file_handler.filename)
        self.assertTrue(self.env["res.partner"].search_count([("name", "=", "Donald Duck")]))

    @mute_logger("xx_log")
    @patch(
        "ftplib.FTP",
        **{
            "return_value.nlst.return_value": ["partner.json"],
        },
    )
    def test_process_ftp_connection_create_partner_failed(self, mock_ftp):
        # Set up a mock retrbinary method
        def mock_retrbinary(command, callback):
            # Simulate the behavior of retrbinary by calling the callback function with the data
            callback(data_to_download)

        # Define the data to be downloaded
        data_to_download = b"{'invalid_field': 'Donald Duck'}"
        # Create a mock FTP instance
        mock_ftp_instance = mock_ftp.return_value
        mock_ftp_instance.retrbinary.side_effect = mock_retrbinary

        ftp_connection = self._create_ftp_connection(GET_DIRECTION)
        ftp_directory = ftp_connection.ftp_directory_ids.filtered(
            lambda d: d.direction == GET_DIRECTION
        )
        ftp_directory.model_id = self.env.ref("base.model_res_partner").id
        ftp_directory.method_name = "create"
        ftp_directory.args = b"[{'invalid_field': 'Donald Duck'}]"
        ftp_connection.test_connection()
        ftp_connection.process_ftp_connections()
        file_handler = self.env["xx.ftp.file.handler"].search(
            [("ftp_connection_directory_id", "=", ftp_directory.id)]
        )
        self.assertTrue(file_handler)
        self.assertEqual(file_handler.state, "new")
        with open(file_handler.filename) as file:
            content = file.read()
        self.assertEqual(content, data_to_download.decode("utf-8"))
        self.ftp_file_handler_obj.process_ftp_files()
        self.assertEqual(file_handler.state, "error")
        self.assertIn("ftp/in/error/partner.json", file_handler.filename)
        self.assertFalse(self.env["res.partner"].search_count([("name", "=", "Donald Duck")]))

    @mute_logger("xx_log")
    @patch(
        "ftplib.FTP",
        **{
            "return_value.nlst.return_value": ["partner.json"],
        },
    )
    def test_process_ftp_connection_delete_directory(self, _mock_ftp):
        ftp_connection = self._create_ftp_connection(GET_DIRECTION)
        ftp_directory = ftp_connection.ftp_directory_ids.filtered(
            lambda d: d.direction == GET_DIRECTION
        )
        ftp_directory.unlink()

    @mute_logger("xx_log")
    @patch("ftplib.FTP")
    @patch("glob.glob")
    @patch("os.path.isfile")
    @patch("builtins.open", create=True)
    @patch("os.rename")
    def test_process_ftp_connection_put(
        self, mock_rename, mock_open, mock_isfile, mock_glob, _mock_ftp
    ):
        # Configure the mock to return a list if files
        mock_glob.return_value = ["foo.txt", "foo2.txt"]
        # Configure the mock to return True
        mock_isfile.return_value = True
        # Configure the mock to return a file-like object
        mock_file = mock_open.return_value
        mock_file.__enter__.return_value.read.return_value = "Mocked File Content"
        # Configure the mock to return a file-like object
        mock_rename.return_value = None
        ftp_connection = self._create_ftp_connection(PUT_DIRECTION)
        ftp_connection.test_connection()
        ftp_connection.process_ftp_connections()

    @mute_logger("xx_log")
    @patch("paramiko.Transport")
    def test_process_sftp_connection_get(self, mock_transport):
        mock_transport.listdir.return_value = ["foo.txt", "foo2.txt"]
        mock_transport.lstat.return_value.st_mode = 1
        mock_transport.lstat.return_value.st_size = 100

        sftp_connection = self._create_sftp_connection(GET_DIRECTION)
        with patch("paramiko.Ed25519Key.from_private_key_file"), patch.object(
            FtpConnection, "get_connection", return_value=mock_transport
        ):
            sftp_connection.test_connection()
            sftp_connection.process_ftp_connections()

    @mute_logger("xx_log")
    @patch("paramiko.Transport")
    def test_process_sftp_connection_get_archive_remote(self, mock_transport):
        mock_transport.listdir.return_value = ["foo.txt", "foo2.txt"]
        mock_transport.lstat.return_value.st_mode = 1
        mock_transport.lstat.return_value.st_size = 100

        sftp_connection = self._create_sftp_connection(GET_DIRECTION)
        sftp_connection.ftp_directory_ids.filtered(
            lambda d: d.direction == GET_DIRECTION
        ).archive_name = "archive/out/"

        with patch("paramiko.Ed25519Key.from_private_key_file"), patch.object(
            FtpConnection, "get_connection", return_value=mock_transport
        ):
            sftp_connection.test_connection()
            sftp_connection.process_ftp_connections()
