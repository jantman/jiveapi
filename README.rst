python-jive-api
===============

Simple and limited Python client for `Jive <https://www.jivesoftware.com/>`_ collaboration software `ReST API v3 <https://developers.jivesoftware.com/api/v3/cloud/rest/index.html>`_.

Status and Limitations
----------------------

I'm writing this to be a working Python wrapper around a small portion of the Jive ReST API - specifically, uploading/publishing blog posts ("Posts" API data type) and uploading/updating Documents. I'm doing this in my personal time, but we'll be using the project at work for a very limited requirement: "syndicating" documentation that we publish on internal web servers to our corporate Jive instance. I don't plan on adding support beyond what's required for that, but contributions are welcome.

Requirements
------------

* Python 3.4+
* `requests <http://docs.python-requests.org/en/master/>`_ package

Installation
------------

TBD.

Authentication
--------------

Version 3 of the Jive ReST API is rather limited in terms of `Authentication methods <https://developer.jivesoftware.com/intro/#building-an-api-client>`_: OAuth is only supported for Jive Add-Ons. The alternative is HTTP Basic, which is not supported for federated/SSO accounts. This project uses HTTP Basic auth, which requires a Jive local (service) account.

Examples - CLI
--------------

TBD.

Examples - Python
-----------------

TBD.

Testing
-------

TBD.

Development
-----------

TBD.

License
-------

This software is licensed under the `Affero General Public License, version 3 or later <https://www.gnu.org/licenses/agpl-3.0.en.html>`_. If you're not redistributing or modifying this software, compliance with the license is simple: make sure anyone interacting with it (even remotely over a network) is informed of where the source code can be downloaded (the project URL in the Python package, or the ``jiveapi.version.PROJECT_URL`` string constant). If you intend on modifying it, the user must have a way of retrieving the exact running source code. If you're intending on distributing it outside your company, please read the full license and consult your legal counsel or Open Source Compliance policy.
