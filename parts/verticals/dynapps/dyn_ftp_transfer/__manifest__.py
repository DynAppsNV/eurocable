{
    "name": "Dynapps FTP Transfer",
    "version": "17.0.1.0.0",
    "category": "Dynapps/Generic module",
    "author": "dynapps",
    "website": "https://www.dynapps.eu",
    "depends": ["base_setup", "dyn_ftp_connection", "dyn_log", "queue_job"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/cron.xml",
        "data/queue.xml",
        "views/ftp_file_handler.xml",
        "views/menus.xml",
        "views/ftp_directories.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
