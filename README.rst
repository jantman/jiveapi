python-jive-api
===============

.. image:: http://www.repostatus.org/badges/latest/wip.svg
   :alt: Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.
   :target: http://www.repostatus.org/#wip

Simple and limited Python client for `Jive <https://www.jivesoftware.com/>`_ collaboration software `ReST API v3 <https://developers.jivesoftware.com/api/v3/cloud/rest/index.html>`_.

Scope and Status
----------------

I'm writing this to be a working Python wrapper around a small portion of the Jive ReST API - specifically, uploading/publishing blog posts ("Posts" API data type) and uploading/updating Documents. I'm doing this in my personal time, but we'll be using the project at work for a very limited requirement: "syndicating" documentation that we publish on internal web servers to our corporate Jive instance. I don't plan on adding support beyond what's required for that, but contributions are welcome.

For the time being, this should be considered Alpha-quality software. It's young and likely only has a handful of code paths exercised on a regular basis, and from what I've seen in practice and in the documentation, I can only assume that Jive has many error conditions this software has yet to see. In short, for the time being, make sure you sanity check things or don't rely on this working 100% of the time. Bug reports are very welcome, but please be sure to include full debugging output.

Supported Actions
+++++++++++++++++

* Low-level API (direct interface to Jive API calls)

  * Get information on currently-authenticated user
  * Get API version information
  * `Get <https://developers.jivesoftware.com/api/v3/cloud/rest/ContentService.html#getContent%28String%2C%20String%2C%20boolean%2C%20List%3CString%3E>`_, `Create <https://developers.jivesoftware.com/api/v3/cloud/rest/ContentService.html#createContent%28String%2C%20String%2C%20String%2C%20String%29>`_, and `Update <https://developers.jivesoftware.com/api/v3/cloud/rest/ContentService.html#updateContent%28String%2C%20String%2C%20String%2C%20boolean%2C%20String%2C%20boolean%29>`_ `Content <https://developers.jivesoftware.com/api/v3/cloud/rest/ContentService.html>`_ (i.e. `Documents <https://developers.jivesoftware.com/api/v3/cloud/rest/DocumentEntity.html>`_, `Posts <https://developers.jivesoftware.com/api/v3/cloud/rest/PostEntity.html>`_, etc.) in Jive from Python dictionary equivalents of the native Jive API `types <https://developers.jivesoftware.com/api/v3/cloud/rest/index.html>`_.
  * `Get binary Image data <https://developers.jivesoftware.com/api/v3/cloud/rest/ImageService.html#getImage%28String%2C%20String%2C%20String%2C%20String%2C%20String%29>`_ and `Create <https://developers.jivesoftware.com/api/v3/cloud/rest/ImageService.html#uploadImage%28MultipartBody%29>`_ `Images <https://developers.jivesoftware.com/api/v3/cloud/rest/ImageEntity.html>`_ that can be embedded in Content (i.e. Documents and Posts).
  * Backdate Content items when creating or updating them.
  * *Not yet implemented:* Upload the above Content types to a Place (i.e. Space, Blog, Group, etc.)

* High-level wrapper API (provides assistance with generating parameters and massaging content):

  * *Not Yet Implemented:* Create and Update HTML Documents or Posts given HTML content and some parameters, including most of the common parameters for the place to post in, visibility, published/draft status, and keywords.
  * *Not Yet Implemented:* Modify HTML formatting to use Jive UI conventions ("jive-ize" HTML).
  * *Not Yet Implemented:* Given a HTML string that contains image tags referring to local images and the filesystem path containing the images, upload each of them to Jive and return the HTML with image paths replaced with their Jive URLs.
  * *Not yet Implemented:* A way to update content that includes embedded Images without updating the images. It doesn't appear that the Jive API returns a checksum for images, but maybe there's a way to get it to?
  * *Not yet implemented:* Option to modify HTML to insert Jive-style information/notice boxes as header and footer, such as information reminding users not to edit the document directly on Jive and giving links to the canonical source, commit, and build that last generated the content.
  * *Not yet implemented:* Uploading "editable" Content that includes Jive macros, such as information boxes and table of contents.

Requirements
------------

* Python 3.4+. Yes, this package is *only* developed and tested against Python3. It *should* work under 2.7 as well, but that is neither tested nor supported.
* `requests <http://docs.python-requests.org/en/master/>`_ package

Installation
------------

``pip install jiveapi``

Authentication
--------------

Version 3 of the Jive ReST API is rather limited in terms of `Authentication methods <https://developer.jivesoftware.com/intro/#building-an-api-client>`_: OAuth is only supported for Jive Add-Ons. The alternative is HTTP Basic, which is not supported for federated/SSO accounts. This project uses HTTP Basic auth, which requires a Jive local (service) account.

Important Notes
---------------

Content IDs
+++++++++++

When a Content object (e.g. Document, Post, etc.) is created in Jive it is assigned a unique contentID. This contentID must be provided in order to update or delete the content. It is up to you, the user, to store the contentIDs generated by this package when you create content objects. For example use it's enough to record them from the CLI output. For actual production use, I recommend using the Python API and storing the returned IDs in a database or key/value store, or committing them back to the git repository. Also note that even though I've never seen a Jive contentID that isn't ``^[0-9]+$``, the Jive API JSON presents and accepts them as strings and the API type documentation lists them as strings.

For most Jive objects, you can obtain the ID by viewing it in the web interface and appending ``/api/v3`` to the URL. i.e. if you have a Space at ``https://sandbox.jiveon.com/community/developertest``, you can find its contentID in the JSON returned from ``https://sandbox.jiveon.com/community/developertest/api/v3``. It is **important** to note that the "id" field of the JSON is *not* the same as the "contentID" field.

HTML
++++

Jive's HTML handling is somewhat strange. First, uploaded HTML for Content (Documents, Posts, etc.) must start at the ``<body>`` tag or lower, not be a full ``<html>`` document or have a ``<head>``. In most Jive installations that I've seen, the HTML needs to be massaged a bit to look correct in Jive. This package does/will include code for that.

Usage
-----

jiveapi contains two main classes, ``JiveApi`` and ``JiveContent``. The ``JiveApi`` class contains the low-level methods that map directly to Jive's API, such as creating and updating Content and Images. These methods generally require dicts (serialized to JSON objects in the API calls) that comply with the Jive API documentation for each object type. The ``JiveContent`` class wraps an instance of ``JiveApi`` and provides higher-level convenience methods for generating these API calls such as posting a string of HTML as a Document in a specific Place. ``JiveContent`` also contains static helper methods, such as for manipulating HTML to appear properly in Jive.

Examples - CLI
--------------

TBD.

Examples - Python
-----------------

See ``jiveapi/cli.py`` for more detailed examples.

Jive Sandbox for Testing
------------------------

If you're interested in trying this against something other than your real Jive instance, Jive maintains `https://sandbox.jiveon.com/ <https://sandbox.jiveon.com/>`_ as a developer sandbox. There should be a "How to Access Sandbox" link in the header; as of the writing of this software, it's a completely automated process that should take less than five minutes (but result in a sales email that you can ignore if you wish).

Testing
-------

Testing is done via `tox <https://tox.readthedocs.io/en/latest/>`_ and `pytest <https://docs.pytest.org/en/latest/>`_. ``pip install tox`` then ``tox`` to run tests.

The package itself uses the wonderful `requests package <http://docs.python-requests.org/en/master/>`_ as a HTTP(S) client. Tests use the `betamax <http://betamax.readthedocs.io/en/latest/index.html>`_ package to record and replay HTTP(S) requests and responses. When adding a new test using betamax, set ``JIVEAPI_TEST_MODE=--record`` in your environment to capture and record new requests - otherwise, outgoing HTTP requests will be blocked. To re-record a test, delete the current capture from ``tests/fixtures/cassettes``. Before committing test data, please inspect it and be sure that no sensitive information is included. To print all base64 bodies from a specific betamax "cassette", you can use ``jiveapi/tests/fixtures/showcassette.py``.

Development
-----------

1. Clone the git repo.
2. ``virtualenv .``
3. ``python setup.py develop``
4. Make changes as necessary. Run tests with ``tox``.

License
-------

This software is licensed under the `Affero General Public License, version 3 or later <https://www.gnu.org/licenses/agpl-3.0.en.html>`_. If you're not redistributing or modifying this software, compliance with the license is simple: make sure anyone interacting with it (even remotely over a network) is informed of where the source code can be downloaded (the project URL in the Python package, or the ``jiveapi.version.PROJECT_URL`` string constant). If you intend on modifying it, the user must have a way of retrieving the exact running source code. If you're intending on distributing it outside your company, please read the full license and consult your legal counsel or Open Source Compliance policy.
