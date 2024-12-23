.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=====================================================
Dynapps Website configuration with server_environment
=====================================================

This module allows to configure website settings using the server_environment mechanism: you can then have different settings for the production and the test environment.

Installation
============

To install this module, you need to have the `server_environment` module installed and properly configured.

Configuration
=============

With this module installed, the website settings can be
configured in the `server_environment_files` module (which is a module
you should provide, see the documentation of `server_environment` for
more information).

Before you can configure the website settings, you need to add the setting to the
`_server_env_fields`

Example ::

    @property
    def _server_env_fields(self):
        base_fields = super()._server_env_fields
        website_fields = {
            "custom_field": {},
        }
        website_fields.update(base_fields)
        return website_fields

Then you can configure the website settings in the configuration file

In the configuration file of each environment, you may first use the
section `[website]` to configure the default values for each website.

Then for each website, you can define additional values or override the
default values with a section named `[website.code]` where "code" is the code of
the website.

Example of config file ::

  [website]
  custom_field = default

  [website.MAIN]
  custom_field = main

  [website.OTHER]
  custom_field = other

You will need to configure the code on the website.

Usage
=====

Once configured, Odoo will read the website values from the
configuration file related to each environment defined in the main
Odoo file.

Bug Tracker
===========

Bugs are tracked on the support page

Credits
=======

Contributors
------------

- Bjorn Billen <bjorn.billen@dynapps.be>

Do not contact contributors directly about support or help with technical issues.

Maintainer
----------

.. image:: dyn_website_environment/static/description/icon.png
   :alt: Dynapps NV
   :target: https://www.dynapps.eu

This module is maintained by Dynapps.
