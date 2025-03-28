===============================
Web Widget Domain Editor Dialog
===============================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:a19a57ea34b8bf09bb11728f135294a703e7b7da461f205bc77a8ce798c2ff0f
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fweb-lightgray.png?logo=github
    :target: https://github.com/OCA/web/tree/17.0/web_widget_domain_editor_dialog
    :alt: OCA/web
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/web-17-0/web-17-0-web_widget_domain_editor_dialog
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/web&target_branch=17.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

Since v11 introduced the new domain editor widget it's not possible to
edit the selected records from the current domain.

This module reintroduces that dialog to complement the current widget
with the powerful search engine of Odoo.

**Table of contents**

.. contents::
   :local:

Usage
=====

In any view with a domain field widget and model, but we'll make the
example with a user filter:

1. Enter debug mode.
2. Go to the *Debug menu* and select the option *Manage Filters*
3. Create a new one
4. Put a name to the filter and select a model (e.g.: Contact)
5. Click on the record selection button and a list dialog opens. There
   you can either:

..

   -  Select individual records: those ids will be added to the domain.
   -  Set filters that will be applied to the domain and select all the
      records to add it as a new filter.
   -  Set groups that will be converted into search filters, select all
      the records and those unfolded groups will be set as filters to.

You can still edit the filter with Odoo's widget after that.

|image1|

.. |image1| image:: https://raw.githubusercontent.com/OCA/web/17.0/web_widget_domain_editor_dialog/static/src/img/behaviour.gif

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/web/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/web/issues/new?body=module:%20web_widget_domain_editor_dialog%0Aversion:%2017.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
-------

* Tecnativa

Contributors
------------

-  `Tecnativa <https://www.tecnativa.com>`__

   -  David Vidal
   -  Jairo Llopis
   -  Carlos Roca

-  Darshan Patel <darshan.barcelona@gmail.com>
-  Helly kapatel <helly.kapatel@initos.com>
-  Carlos Lopez <celm1990@gmail.com>

Maintainers
-----------

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/web <https://github.com/OCA/web/tree/17.0/web_widget_domain_editor_dialog>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
