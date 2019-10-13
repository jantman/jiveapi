jiveapi python package
======================

.. image:: https://secure.travis-ci.org/jantman/jiveapi.png?branch=master
   :target: http://travis-ci.org/jantman/jiveapi
   :alt: travis-ci for master branch

.. image:: https://readthedocs.org/projects/jiveapi/badge/?version=latest
   :target: https://readthedocs.org/projects/jiveapi/?badge=latest
   :alt: sphinx documentation for latest release

.. image:: https://www.repostatus.org/badges/latest/unsupported.svg
   :alt: Project Status: Unsupported – The project has reached a stable, usable state but the author(s) have ceased all work on it. A new maintainer may be desired.
   :target: https://www.repostatus.org/#unsupported

Simple and limited Python client for `Jive <https://www.jivesoftware.com/>`_ collaboration software `ReST API v3 <https://developers.jivesoftware.com/api/v3/cloud/rest/index.html>`_, along with utilities for massaging HTML to display better on Jive. Also comes pre-installed in a Docker image and a Sphinx theme and builder for Jive-optimized HTML output.

**Note: Full documentation is hosted at:** `jiveapi.readthedocs.io <http://jiveapi.readthedocs.io/>`_. **This README is just a short introduction.**

Scope and Status
----------------

**This project is effectively abandoned/unsupported and needs a new maintainer!** My employer to longer uses Jive, so I'm no longer using this project and also have no way of testing it. If you are interested in taking over as maintainer, please open an issue!

I'm writing this to be a working Python wrapper around a small portion of the Jive ReST API - specifically, uploading/publishing updating Documents, uploading embedded Images, and manipulating the input HTML to display better in Jive. I'm doing this in my personal time, but we'll be using the project at work for a very limited requirement: "syndicating" documentation that we publish on internal web servers (mostly Sphinx and Hugo static sites) to our corporate Jive instance. The main purpose for doing this is to reach a wider audience and for searchability, not to faithfully reproduce the layout and styling of the original HTML. I don't plan on adding support beyond what's required for that, but contributions are welcome.

This has been in use daily at my current employer for almost a year. It's stable for the particular way we use it, but some code paths may not have been fully exercised before.

Also be aware that Jive **heavily modifies** HTML, including stripping out and sometimes replacing ``id`` attributes, breaking any internal anchor links containing dashes, etc. The high-level methods in this package make a best effort to modify HTML to work in Jive, but nothing is guaranteed. Once again, this is focused on content not presentation.

Supported Actions
+++++++++++++++++

* Low-level API (direct interface to Jive API calls)

  * Get information on currently-authenticated user
  * Get API version information
  * `Get Content <https://developers.jivesoftware.com/api/v3/cloud/rest/ContentService.html#getContent%28String%2C%20String%2C%20boolean%2C%20List%3CString%3E%29>`_, `Create Content <https://developers.jivesoftware.com/api/v3/cloud/rest/ContentService.html#createContent%28String%2C%20String%2C%20String%2C%20String%29>`_, and `Update Content <https://developers.jivesoftware.com/api/v3/cloud/rest/ContentService.html#updateContent%28String%2C%20String%2C%20String%2C%20boolean%2C%20String%2C%20boolean%29>`_ (i.e. `Documents <https://developers.jivesoftware.com/api/v3/cloud/rest/DocumentEntity.html>`_, `Posts <https://developers.jivesoftware.com/api/v3/cloud/rest/PostEntity.html>`_, etc.) in Jive from Python dictionary equivalents of the native Jive API `types <https://developers.jivesoftware.com/api/v3/cloud/rest/index.html>`_.
  * `Get binary Image data <https://developers.jivesoftware.com/api/v3/cloud/rest/ImageService.html#getImage%28String%2C%20String%2C%20String%2C%20String%2C%20String%29>`_ and `Create <https://developers.jivesoftware.com/api/v3/cloud/rest/ImageService.html#uploadImage%28MultipartBody%29>`_ `Images <https://developers.jivesoftware.com/api/v3/cloud/rest/ImageEntity.html>`_ that can be embedded in Content (i.e. Documents and Posts).
  * Backdate Content items when creating or updating them.
  * List all Content in a `Place <https://developers.jivesoftware.com/api/v3/cloud/rest/PlaceService.html>`_.

* High-level wrapper API (provides assistance with generating parameters and massaging content):

  * Create and Update HTML Documents given HTML content and some parameters, including most of the common parameters such as the place to post in, visibility, published/draft status, and keywords.
  * *Not Yet Implemented:* Create and Update HTML Posts given HTML content and some parameters, including most of the common parameters such as the place to post in, visibility, published/draft status, and keywords.
  * Modify HTML formatting to use Jive UI conventions ("jive-ize" HTML).
  * Given a HTML string that contains image tags referring to local images and the filesystem path containing the images, upload each of them to Jive and modify the HTML to point to the images' Jive URLs. Return metadata about the content and images to the user for future updates. Use this metadata on future updates to prevent re-uploading the same image.
  * Option to modify HTML to insert Jive-style information/notice boxes as header and footer, such as information reminding users not to edit the document directly on Jive and giving links to the canonical source, commit, and build that last generated the content.
  * Option to add a Jive Table of Contents macro to the beginning of the content.

* jiveapi also includes a basic `Sphinx <http://www.sphinx-doc.org>`_ theme (called ``jiveapi``) and Builder (also called ``jiveapi``) optimized for building single-page HTML for uploading to Jive.

Requirements
------------

jiveapi is also available in a self-contained Docker image with all dependencies. See `https://hub.docker.com/r/jantman/jiveapi/ <https://hub.docker.com/r/jantman/jiveapi/>`_.

* Python 3.4+. Yes, this package is *only* developed and tested against Python3, specifically 3.4 or later. It *should* work under 2.7 as well, but that is neither tested nor supported.
* `requests <https://requests.kennethreitz.org/en/master/>`_
* `premailer <http://github.com/peterbe/premailer>`_ (optional, only required for high-level JiveContent interface)
* `lxml <http://lxml.de/>`_ (optional, only required for high-level JiveContent interface)

Usage
-----

**See the full documentation at:** `http://jiveapi.readthedocs.io/ <http://jiveapi.readthedocs.io/>`_

License
-------

This software is licensed under the `Affero General Public License, version 3 or later <https://www.gnu.org/licenses/agpl-3.0.en.html>`_. If you're not redistributing or modifying this software, compliance with the license is simple: make sure anyone interacting with it (even remotely over a network) is informed of where the source code can be downloaded (the project URL in the Python package, or the ``jiveapi.version.PROJECT_URL`` string constant). If you intend on modifying it, the user must have a way of retrieving the exact running source code. If you're intending on distributing it outside your company, please read the full license and consult your legal counsel or Open Source Compliance policy.
