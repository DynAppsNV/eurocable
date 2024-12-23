.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=====================================================
Dynapps Company configuration with server_environment
=====================================================

This module allows to configure company settings using the server_environment mechanism: you can then have different settings for the production and the test environment.

Installation
============

To install this module, you need to have the `server_environment` and `res_company_code` modules installed and properly configured.

Configuration
=============

With this module installed, the company settings can be
configured in the `server_environment_files` module (which is a module
you should provide, see the documentation of `server_environment` for
more information).

Before you can configure the company settings, you need to add the setting to the
`_server_env_fields`

Example ::

    @property
    def _server_env_fields(self):
        base_fields = super()._server_env_fields
        company_fields = {
            "custom_field": {},
        }
        company_fields.update(base_fields)
        return company_fields

Then you can configure the company settings in the configuration file

In the configuration file of each environment, you may first use the
section `[res.company]` to configure the default values for each company.

Then for each company, you can define additional values or override the
default values with a section named `[res.company.code]` where "code" is the code of
the company.

Example of config file ::

  [res.company]
  custom_field = default

  [res.company.MAIN]
  custom_field = main

  [res.company.OTHER]
  custom_field = other

You will need to configure the code on the company.

Usage
=====

Once configured, Odoo will read the company values from the
configuration file related to each environment defined in the main
Odoo file.

Bug Tracker
===========

Bugs are tracked on the support page

Credits
=======

Contributors
------------

- Raf Ven <raf.ven@dynapps.be>

Do not contact contributors directly about support or help with technical issues.

Maintainer
----------

.. image:: dyn_company_environment/static/description/icon.png
   :alt: Dynapps NV
   :target: https://www.dynapps.eu

This module is maintained by Dynapps.
