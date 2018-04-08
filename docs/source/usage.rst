.. _usage_and_examples:

Usage and Examples
==================

.. _return-dict-format:

JiveContent Return Dict Format
------------------------------

The :py:class:`~.JiveContent` high-level wrapper methods that create or update content in Jive (specifically :py:meth:`~.JiveContent.create_html_document` and :py:meth:`~.JiveContent.update_html_document`) return a dictionary describing the content object that was created and various Jive attributes of it. This dict includes the ``contentID``, which Jive uses to uniquely identify content objects and must be known in order to update content in Jive. It also contains an ``images`` key, described below under :ref:`JiveContent Images Dict Format <images-dict-format>`, that must be known in order to not re-upload all images when content is updated.

This dict **must be persisted** if you want to programmatically update the content object in the future. The format of the dict is as follows:

``entityType`` : *(string)*
    the entityType of the content object in Jive.

``id`` : *(string)*
    the ID of the content in Jive. This is only used internally to Jive and is distinct from the ``contentID``.

``html_ref`` : *(string)*
    the URL to the content object in the Jive UI, i.e. the URL for users to access it at. Can possibly be an empty string.

``contentID`` : *(string)*
    the Jive content ID required to update this content object; must be passed in when updating existing content. While these IDs appear to only contain numeric characters, the Jive API documentation explicitly states that they are strings.

``type`` : *(string)*
    the content type of the object, i.e. ``document`` or ``post``.

``typeCode`` : *(int)*
    the numeric content type code of the object.

``images`` : *(dict)*
    information about the images contained in the content that have already been uploaded. Details are in :ref:`JiveContent Images Dict Format <images-dict-format>`, below.

Aside from ``images``, all of the values are taken from the Jive API representation of the content object; see `Jive ReST API - Content Entity <https://developers.jivesoftware.com/api/v3/cloud/rest/ContentEntity.html>`_ for further information.

.. _images-dict-format:

JiveContent Images Dict Format
------------------------------

When images are uploaded in Jive, they are assigned unique identifiers. There is no simple way to determine if an image has already been uploaded to Jive (i.e. the system does not store, or at least does not expose via the API, any sort of checksum). As such, to prevent uploading the same image (as a new Jive object) on every update of a content object, we must store information about the images already uploaded for a given content object and determine on the client side if an image already exists in Jive.

The ``images`` dict, returned as the value of the ``images`` key of the :ref:`JiveContent Return Dict Format <return-dict-format>`, stores this information.

Keys of this dict are the string hexdigest of the sha256 checksum of the image's binary content, as returned by passing the image's content through :py:mod:`hashlib.sha256 <hashlib>` (see :py:meth:`~.JiveContent._load_image_from_disk` for implementation). Values are dicts describing the image, namely:

``location`` : *(string)*
    The URI to the binary image itself as returned by Jive when uploading the image. This is the URI used when embedding the image in HTML.

``jive_object`` : *(dict)*
    The Image Object returned by Jive when uploading the image; see the `Jive ReST API - Image Entity <https://developers.jivesoftware.com/api/v3/cloud/rest/ImageEntity.html>`_ for details.

``local_path`` : *(string)*
    The original local path to the image in input HTML, i.e. the ``src`` attribute of the image tag in the original HTML passed to :py:class:`~.JiveContent`.

If this dict is not persisted by the client and passed back in on subsequent method calls that update the content, images will be re-uploaded as distinct Jive objects every time.

.. _usage:

Usage
-----

jiveapi contains two main classes, :py:class:`~.JiveApi` and :py:class:`~.JiveContent`. The :py:class:`~.JiveApi` class contains the low-level methods that map directly to `Jive's API <https://developers.jivesoftware.com/api/v3/cloud/rest/index.html>`_, such as creating and updating `Content <https://developers.jivesoftware.com/api/v3/cloud/rest/ContentEntity.html>`_ and `Images <https://developers.jivesoftware.com/api/v3/cloud/rest/ImageEntity.html>`_. These methods generally require dicts (serialized to JSON objects in the API calls) that comply with the Jive API documentation for each object type. The :py:class:`~.JiveContent` class wraps an instance of :py:class:`~.JiveApi` and provides higher-level convenience methods for generating these API calls such as posting a string of HTML as a `Document <https://developers.jivesoftware.com/api/v3/cloud/rest/DocumentEntity.html>`_ in a specific Place. :py:class:`~.JiveContent` also contains static helper methods, such as for manipulating HTML to appear properly in Jive.

.. _examples:

Examples
--------

For examples of the use of the low-level methods in :py:class:`~.JiveApi`, see the source code of the unit tests and of the high-level :py:class:`~.JiveContent` class.

Uploading HTML as a Document
++++++++++++++++++++++++++++

In this example we assume that we have a HTML file, ``index.html``, in our current directory that we want to upload to the Jive server at ``http://jive.example.com`` as a Document. If the HTML contains any images, they are either in our current directory or have paths relative to our current directory.

.. code-block:: python

    import json
    from jiveapi import JiveApi, JiveContent
    api = JiveApi('http://jive.example.com', 'username', 'password')
    jive = JiveContent(api)
    with open('index.html', 'r') as fh:
        html = fh.read()
    res = jive.create_html_document('My Title', html)
    with open('jive_document.json', 'w') as fh:
        fh.write(json.dumps(res))

Note that we have JSON-serialized the return value of :py:meth:`~.JiveContent.create_html_document`, which is a dict in the :ref:`JiveContent Return Dict Format <return-dict-format>`. We will need this information when updating the Document in the future; this example just writes it to a file in the current directory, but any non-trivial use should probably store it in a database or key/value store.

Updating an Existing Document
+++++++++++++++++++++++++++++

Following on the previous example, let's assume that we've made some edits to the HTML and replaced one of the images in it and want to make those changes in Jive. We'll use the :py:meth:`~.JiveContent.update_html_document` method for this:

.. code-block:: python

    import json
    from jiveapi import JiveApi, JiveContent
    api = JiveApi('http://jive.example.com', 'username', 'password')
    jive = JiveContent(api)
    with open('index.html', 'r') as fh:
        html = fh.read()
    with open('jive_document.json', 'r') as fh:
        doc = json.loads(fh.read())
    res = jive.update_html_document(doc['contentID'], 'My Title', html, images=doc['images'])
    with open('jive_document.json', 'w') as fh:
        fh.write(json.dumps(res))

We should now have a properly-updated document in Jive. This process only uploads new images.

Notable Options
+++++++++++++++

The :py:meth:`~.JiveContent.create_html_document` and :py:meth:`~.JiveContent.update_html_document` methods share many common options. See their documentation for the full list, but here are some that may be of particular interest:

tags : *(list*)
    a list of string tags to add to the content

place_id : *(string)*
    the ID of a Place to create the content in. This can be obtained by browsing to a place in the Jive UI and appending ``/api/v3`` to the URL.

set_datetime : *(datetime.datetime)*
    the Jive API allows you to explicitly specify the creation/update date on content, i.e. for use when migrating content in.

toc : *(boolean)*
    prepend the Jive Table of Contents macro to the content.

header_alert : *(str or tuple)*
    prepend a Jive Alert Box macro to the content, such as to remind users that it was created by an external system.

footer_alert : *(str or tuple)*
    append a Jive Alert Box macro to the content, such as to link to the build that updated it.

.. _docker_examples:

Docker Examples
---------------

The `jiveapi Docker image <https://hub.docker.com/r/jantman/jiveapi/>`_ is an Alpine Linux / Python 3.6 image that comes with jiveapi, Sphinx, the Read The Docs Sphinx theme, rinohtype and boto3. They are all installed globally. The default entrypoint of the container is ``/bin/bash``, dropping you into a root shell so that you can explore (i.e. run ``python``). For normal use, you would most likely write a script in your current working directory to do whatever you need, mount your current working directory into the container, and then run that script.

For instance, one of the above examples could be saved as ``./jive_upload.py`` and then run in the Docker container with:

.. code-block:: bash

    docker run -it --rm -v $(pwd):/app jantman/jiveapi:0.1.0 bash -c 'cd /app && python jive_upload.py'

Please keep in mind that, since the container runs as root, any files it writes to your current directory will be owned by root.

.. _sphinx_usage:

Sphinx Theme and Builder
------------------------

This package includes a `Sphinx <http://www.sphinx-doc.org/>`_ theme and builder that generate single-page HTML output optimized for uploading to Jive via jiveapi. The theme is based on sphinx' :ref:`built-in "basic" theme <builtin-themes>` and the builder is based on sphinx' built-in :py:class:`~sphinx.builders.html.SingleFileHTMLBuilder`.

To build your existing Sphinx documentation you need only install the jiveapi package and specify the "jiveapi" theme and "jiveapi" builder. For example, if your documentation source is in the ``source/`` directory, then you could build a single-page jive-optimized HTML file to ``jivehtml/index.html`` with:

.. code-block:: bash

    python -msphinx source jivehtml -b jiveapi -D html_theme=jiveapi

.. _jive_sandbox:

Jive Sandbox for Testing
------------------------

If you're interested in trying this against something other than your real Jive instance, Jive maintains `https://sandbox.jiveon.com/ <https://sandbox.jiveon.com/>`_ as a developer sandbox. There should be a `How to Access Sandbox <https://community.jivesoftware.com/docs/DOC-172438>`_ link in the header; as of the writing of this software, it's a completely automated process that should take less than five minutes (but result in a sales email that you can ignore if you wish). Be aware that the sandbox seems to be rather unstable and prone to outages and seemingly-random 500 errors.
