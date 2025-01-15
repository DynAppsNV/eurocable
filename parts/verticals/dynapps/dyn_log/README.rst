.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==================
Dynapps DB Logging
==================

Log handler writing to the database.

In your code:

* from odoo.addons.dyn_log.models.db_handler import DBLogger
* logger = DBLogger(cursor, model_name, res_id, uid)

You can create a log entry in the database with a unique pid per logger, by using one of these
methods:

* logger.debug(your_message): debug message
* logger.info(your_message): informational message
* logger.warning(your_message): warning message
* logger.log(your_message): log message
* logger.error(your_message): error message
* logger.critical(your_message): critical error message (includes full stack trace)
* logger.exception(your_message): exception message (includes full stack trace)
* logger.time_info(your_message): information message (includes timestamp)
* logger.time_debug(your_message): debug message (includes timestamp)

Installation
============

To install this module, you need to:

#. Press Install

Configuration
=============

No special configuration needed

Known issues / Roadmap
======================

Bug Tracker
===========

Bugs are tracked on the support page

Credits
=======

Contributors
------------

* Axel Priem <axel.priem@dynapps.be>
* Raf Ven <raf.ven@dynapps.be>

Do not contact contributors directly about support or help with technical issues.

Maintainer
----------

.. image:: dyn_log/static/description/icon.png
   :alt: Dynapps NV
   :target: https://www.dynapps.eu

This module is maintained by Dynapps.
