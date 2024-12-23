{
    "name": "Dynapps FTP Connection",
    "version": "17.0.1.0.0",
    "category": "Dynapps/Generic module",
    "author": "dynapps",
    "website": "https://www.dynapps.eu",
    "depends": ["base_setup"],
    "external_dependencies": {
        "python": ["paramiko"],
    },
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/ftp.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
