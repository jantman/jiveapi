"""
The latest version of this package is available at:
<http://github.com/jantman/jiveapi>

##################################################################################
Copyright 2017 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of jiveapi, also known as jiveapi.

    jiveapi is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    jiveapi is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with jiveapi.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
##################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/jiveapi> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
##################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
##################################################################################
"""

import os
import logging
import imghdr
import hashlib

from lxml import etree
from premailer import Premailer
from urllib.parse import urlparse

from jiveapi.version import VERSION, PROJECT_URL

logger = logging.getLogger(__name__)

#: This is a mapping of certain HTML tags to the Jive styles to apply to them.
TAGSTYLES = {
    'h1': 'color:#24292e; padding-bottom: 0.3em; font-size: 2em; '
          'border-bottom: 1px solid #eaecef',
    'h2': 'color:#24292e; margin-top: 24px; margin-bottom: 16px; '
          'font-weight: 600; line-height: 1.25; padding-bottom: 0.3em; '
          'font-size: 1.5em; border-bottom: 1px solid #eaecef;',
    'h3': 'color:#24292e; font-size: 1.25em; margin-top: 24px; '
          'margin-bottom: 16px; font-weight: 600; line-height: 1.25;',
    'h4': 'color:#24292e; font-size: 1em; margin-top: 24px; '
          'margin-bottom: 16px; font-weight: 600; line-height: 1.25;',
    'h5': 'color:#24292e; font-size: 0.8em; margin-top: 24px; '
          'margin-bottom: 16px; font-weight: 600; line-height: 1.25;',
    'p':  'color:#24292e; margin-top: 0; margin-bottom: 16px;',
    'ul': 'color:#24292e; padding-left: 2em; margin-top: 0; '
          'margin-bottom: 16px;',
    'ol': 'color:#24292e; padding-left: 2em; margin-top: 0; '
          'margin-bottom: 16px;',
    'blockquote': 'padding: 0 1em; color: #6a737d; '
                  'border-left: 0.25em solid #dfe2e5; margin-top: 0; '
                  'margin-bottom: 16px;',
    'img': 'max-width:100%; box-sizing:content-box;',
    'pre': 'word-wrap: normal; padding: 16px; overflow: auto; font-size: 85%; '
           'line-height: 1.45; background-color: #f6f8fa; border-radius: 3px; '
           'margin-top:2px',
    'code': 'display: inline; max-width: auto; padding: 0; margin: 0; '
            'overflow: visible; line-height: inherit; word-wrap: normal; '
            'background-color: transparent; border: 0;',
    'table': 'display: block; width: 100%; overflow: auto;',
    'thead': 'display: table-header-group; vertical-align: middle; '
             'border-color: inherit;',
    'tbody': 'display: table-row-group; vertical-align: middle; '
             'border-color: inherit;',
    'tr': 'background-color: #fff; border-top: 1px solid #c6cbd1;',
    'td': 'padding: 6px 13px; border: 1px solid #dfe2e5; ',
    'th': 'padding: 6px 13px; border: 1px solid #dfe2e5; font-weight: 600; '
          'text-align: center;background-color: #f6f8fa; '
}


def newline_to_br(elem):
    """
    Helper function for :py:meth:`~.JiveContent.jiveize_html`.
    Given a html Element, convert it to a string, add explicit <br /> tags
    before all newlines, and return a new Element with that content.

    :param elem: element to modify
    :type elem: ``lxml.etree._Element``
    :return: modified element
    :rtype: ``lxml.etree._Element``
    """
    src = etree.tostring(elem).strip()
    if isinstance(src, type(b'')):  # nocoverage
        src = src.decode()
    res = src.replace("\n", "<br/>\n")
    return etree.fromstring(res + "\n")


class JiveContent(object):
    """
    High-level Jive API interface that wraps :py:class:`~.JiveApi` with
    convenience methods for common tasks relating to manipulating
    `Content <https://developers.jivesoftware.com/api/v3/cloud/rest/ContentEntit
    y.html>`_ and `Image <https://developers.jivesoftware.com/api/v3/cloud/rest
    /ImageEntity.html>`_ objects.

    Methods in this class that involve uploading images require storing state
    out-of-band. For information on that state, see
    :ref:`JiveContent Images Dict Format <images-dict-format>`.
    """

    def __init__(self, api, image_dir=None):
        """
        :param api: authenticated API instance
        :type api: jiveapi.api.JiveApi
        :param image_dir: The directory/path on disk to load images relative to.
          This should be an absolute path. If not specified, the result of
          :py:func:`os.getcwd` will be used.
        :type image_dir: str
        """
        self._api = api
        if image_dir is None:
            self._image_dir = os.getcwd()
        else:
            self._image_dir = image_dir
        logger.debug(
            'Initializing JiveContent with image_dir=%s', self._image_dir
        )

    def create_html_document(
        self, subject, html, tags=[], place_id=None, visibility=None,
        set_datetime=None, inline_css=True, jiveize=True, handle_images=True
    ):
        """
        Create a HTML `Document <https://developers.jivesoftware.com/api/v3/clou
        d/rest/DocumentEntity.html>`_ in Jive. This is a convenience wrapper
        around :py:meth:`~.create_content` to assist with forming the content
        JSON, as well as to assist with HTML handling.

        The format of the second element of the return value is the images dict
        format described in this class under
        :ref:`JiveContent Images Dict Format <images-dict-format>`.

        **Important:** In order to update the Document in the future, the entire
        return value of this method must be externally persisted and passed in
        to future method calls via the ``content_id`` and ``images``
        parameters.

        :param subject: The subject / title of the Document.
        :type subject: str
        :param html: The HTML for the Document's content. See the notes in the
          jiveapi package documentation about HTML handling.
        :type html: str
        :param tags: List of string tags to add to the Document
        :type tags: list
        :param place_id: If specified, post this document in the Place with the
          specified placeID. According to the API documentation for the Document
          type (linked above), this requires visibility to be set to "place".
        :type place_id: str
        :param visibility: The visibility policy for the Document. Valid values
          per the API documentation are: ``all`` (anyone with appropriate
          permissions can see the content), ``hidden`` (only the author can see
          the content), or ``place`` (place permissions specify which users can
          see the content).
        :type visibility: str
        :param set_datetime: datetime.datetime to set as the publish time. This
          allows backdating Documents to match their source publish time.
        :type set_datetime: datetime.datetime
        :param inline_css: if True, pass input HTML through
          :py:meth:`~.inline_css_etree` to convert any embedded CSS to inline
          CSS so that Jive will preserve/respect it.
        :type inline_css: bool
        :param jiveize: if True, pass input HTML through
          :py:meth:`~.jiveize_etree` to make it look more like how Jive styles
          HTML internally.
        :type jiveize: bool
        :param handle_images: if True, pass input HTML through
          :py:meth:`~._upload_images` to upload all local images to Jive.
        :type handle_images: bool
        :return: 2-tuple of (``dict`` representation of the created Document
          from the Jive API, ``dict`` images data to persist for updates)
        :rtype: tuple
        :raises: RequestFailedException, ContentConflictException
        """
        logger.debug('Generating API call dict for content')
        content, images = self.dict_for_html_document(
            subject, html, tags=tags, place_id=place_id, visibility=visibility,
            inline_css=inline_css, jiveize=jiveize, handle_images=handle_images
        )
        logger.debug('API call dict ready to send')
        if set_datetime is not None:
            res = self._api.create_content(content, publish_date=set_datetime)
        else:
            res = self._api.create_content(content)
        return {
            'entityType': res['entityType'],
            'id': res['id'],
            'html_ref': res.get('resources', {}).get('html', {}).get('ref', ''),
            'contentID': res['contentID'],
            'type': res['type'],
            'typeCode': res['typeCode'],
            'images': images
        }

    def update_html_document(
        self, content_id, subject, html, tags=[], place_id=None,
        visibility=None, set_datetime=None, inline_css=True, jiveize=True,
        handle_images=True, images={}
    ):
        """
        Update a HTML `Document <https://developers.jivesoftware.com/api/v3/clou
        d/rest/DocumentEntity.html>`_ in Jive. This is a convenience wrapper
        around :py:meth:`~.update_content` to assist with forming the content
        JSON, as well as to assist with HTML handling.

        The format of the second element of the return value is the images dict
        format described in this class under
        :ref:`JiveContent Images Dict Format <images-dict-format>`.

        **Important:** In order to update the Document in the future, the entire
        return value of this method must be externally persisted and passed in
        to future method calls via the ``content_id`` and ``images``
        parameters.

        :param content_id: the Jive contentID to update
        :type content_id: str
        :param subject: The subject / title of the Document.
        :type subject: str
        :param html: The HTML for the Document's content. See the notes in the
          jiveapi package documentation about HTML handling.
        :type html: str
        :param tags: List of string tags to add to the Document
        :type tags: list
        :param place_id: If specified, post this document in the Place with the
          specified placeID. According to the API documentation for the Document
          type (linked above), this requires visibility to be set to "place".
        :type place_id: str
        :param visibility: The visibility policy for the Document. Valid values
          per the API documentation are: ``all`` (anyone with appropriate
          permissions can see the content), ``hidden`` (only the author can see
          the content), or ``place`` (place permissions specify which users can
          see the content).
        :type visibility: str
        :param set_datetime: datetime.datetime to set as the publish time. This
          allows backdating Documents to match their source publish time.
        :type set_datetime: datetime.datetime
        :param inline_css: if True, pass input HTML through
          :py:meth:`~.inline_css_etree` to convert any embedded CSS to inline
          CSS so that Jive will preserve/respect it.
        :type inline_css: bool
        :param jiveize: if True, pass input HTML through
          :py:meth:`~.jiveize_etree` to make it look more like how Jive styles
          HTML internally.
        :type jiveize: bool
        :param handle_images: if True, pass input HTML through
          :py:meth:`~._upload_images` to upload all local images to Jive.
        :type handle_images: bool
        :param images: a dict of information about images that have been already
          uploaded for this Document. This parameter should be the value of the
          ``images`` key from the return value of this method or of
          :py:meth:`~.create_html_content`.
        :type images: dict
        :return: 2-tuple of (``dict`` representation of the updated Document
          from the Jive API, ``dict`` images data to persist for updates)
        :rtype: tuple
        :raises: RequestFailedException, ContentConflictException
        """
        logger.debug('Generating API call dict for content')
        content, images = self.dict_for_html_document(
            subject, html, tags=tags, place_id=place_id, visibility=visibility,
            inline_css=inline_css, jiveize=jiveize, handle_images=handle_images,
            images=images
        )
        logger.debug('API call dict ready to send')
        if set_datetime is not None:
            res = self._api.update_content(
                content_id, content, update_date=set_datetime
            )
        else:
            res = self._api.update_content(content_id, content)
        return {
            'entityType': res['entityType'],
            'id': res['id'],
            'html_ref': res.get('resources', {}).get('html', {}).get('ref', ''),
            'contentID': res['contentID'],
            'type': res['type'],
            'typeCode': res['typeCode'],
            'images': images
        }

    def dict_for_html_document(
        self, subject, html, tags=[], place_id=None, visibility=None,
        inline_css=True, jiveize=True, handle_images=True, images={}
    ):
        """
        Generate the API (dict/JSON) representation of a HTML
        `Document <https://developers.jivesoftware.com/api/v3/cloud/rest/Documen
        tEntity.html>`_ in Jive, used by :py:meth:`~.create_html_document`.

        The format of the second element of the return value is the images dict
        format described in this class under
        :ref:`JiveContent Images Dict Format <images-dict-format>`.

        **Important:** The images dict (second element of return value) must be
        externally persisted or else all images will be re-uploaded every time
        this is run.

        :param subject: The subject / title of the Document.
        :type subject: str
        :param html: The HTML for the Document's content. See the notes in the
          jiveapi package documentation about HTML handling.
        :type html: str
        :param tags: List of string tags to add to the Document
        :type tags: list
        :param place_id: If specified, post this document in the Place with the
          specified placeID. According to the API documentation for the Document
          type (linked above), this requires visibility to be set to "place".
        :type place_id: str
        :param visibility: The visibility policy for the Document. Valid values
          per the API documentation are: ``all`` (anyone with appropriate
          permissions can see the content), ``hidden`` (only the author can see
          the content), or ``place`` (place permissions specify which users can
          see the content).
        :type visibility: str
        :param set_datetime: datetime.datetime to set as the publish time. This
          allows backdating Documents to match their source publish time.
        :type set_datetime: datetime.datetime
        :param inline_css: if True, pass input HTML through
          :py:meth:`~.inline_css_etree` to convert any embedded CSS to inline
          CSS so that Jive will preserve/respect it.
        :type inline_css: bool
        :param jiveize: if True, pass input HTML through
          :py:meth:`~.jiveize_etree` to make it look more like how Jive styles
          HTML internally.
        :type jiveize: bool
        :param handle_images: if True, pass input HTML through
          :py:meth:`~._upload_images` to upload all local images to Jive.
        :type handle_images: bool
        :param images: a dict of information about images that have been already
          uploaded for this Document. This parameter should be the value of the
          ``images`` key from the return value of this method (or of
          :py:meth:`~.create_html_content` or :py:meth:`~.update_html_content`).
        :type images: dict
        :return: 2-tuple of (``dict`` representation of the desired Document
          ready to pass to the Jive API, ``dict`` images data to persist for
          updates)
        :rtype: tuple
        """
        if jiveize or inline_css or handle_images:
            logger.debug('Converting input HTML to etree')
            doc = JiveContent.html_to_etree(html)
            if inline_css:
                logger.debug('Passing input HTML through inline_css_etree()')
                doc = JiveContent.inline_css_etree(doc)
            if jiveize:
                logger.debug('Passing input HTML through jiveize_etree()')
                doc = JiveContent.jiveize_etree(doc)
            if handle_images:
                logger.debug('Passing input HTML through _upload_images()')
                doc, images = self._upload_images(doc, images)
            html = etree.tostring(doc)
        if isinstance(html, type(b'')):
            logger.debug('decode() etree.tostring() output')
            html = html.decode()
        content = {
            'type': 'document',
            'subject': subject,
            'content': {
                'type': 'text/html',
                'text': html
            },
            'via': {
                'displayName': 'Python jiveapi v%s' % VERSION,
                'url': PROJECT_URL
            }
        }
        if len(tags) > 0:
            content['tags'] = tags
        if place_id is not None:
            content['parent'] = self._api.abs_url(
                'core/v3/places/%s' % place_id
            )
        if visibility is not None:
            content['visibility'] = visibility
        return content, images

    @staticmethod
    def html_to_etree(html):
        """
        Given a string of HTML, parse via ``etree.fromstring()`` and return
        either the roottree if a doctype is present or the root otherwise.

        **Important Note:** If the document passed in has a doctype, it will be
        stripped out. That's fine, since Jive wouldn't recognize it anyway.

        :param html: HTML string
        :type html: str
        :return: root of the HTML tree for parsing and manipulation purposes
        :rtype: ``lxml.etree._Element`` or ``lxml.etree._ElementTree``
        """
        tree = etree.fromstring(html.strip(), etree.HTMLParser()).getroottree()
        return tree.getroot()

    @staticmethod
    def inline_css_html(html):
        """
        Wrapper around :py:meth:`~.inline_css_etree` that takes a string of HTML
        and returns a string of HTML.

        :param html: input HTML to inline CSS in
        :type html: str
        :return: HTML with embedded/internal CSS inlined
        :rtype: str
        """
        return etree.tostring(
            JiveContent.inline_css_etree(JiveContent.html_to_etree(html))
        )

    @staticmethod
    def inline_css_etree(root):
        """
        Given an etree root node, uses
        `premailer's <http://github.com/peterbe/premailer>`_ ``transform``
        method to convert all CSS from embedded/internal/external to inline, as
        Jive only allows inline CSS.

        :param root: root node of etree to inline CSS in
        :type root: ``lxml.etree._Element``
        :return: root node of etree with CSS inlined
        :rtype: ``lxml.etree._Element`` or ``lxml.etree._ElementTree``
        """
        return Premailer(root).transform()

    @staticmethod
    def jiveize_html(html, no_sourcecode_style=True):
        """
        Wrapper around :py:meth:`~.jiveize_etree` that takes a string of HTML
        and returns a string of HTML.

        :param html: input HTML to Jive-ize
        :type html: str
        :param no_sourcecode_style: If True, remove the ``style`` attribute from
          any ``div`` elements with a class of ``sourceCode``.
        :type no_sourcecode_style: bool
        :return: jive-ized HTML
        :rtype: str
        """
        root = JiveContent.html_to_etree(html)
        return etree.tostring(
            JiveContent.jiveize_etree(
                root, no_sourcecode_style=no_sourcecode_style
            )
        )

    @staticmethod
    def jiveize_etree(root, no_sourcecode_style=True):
        """
        Given a lxml etree root, perform some formatting and style fixes to get
        each element in it to render correctly in the Jive UI:

        * If ``no_sourcecode_style`` is True, remove the ``style`` attribute
          from any ``div`` elements with a class of ``sourceCode``.
        * In all ``<pre>`` elements, convert ``\\n`` to ``<br />\\n``
          via :py:func:`~.newline_to_br`.
        * For any HTML tags that are keys of :py:data:`~.TAGSTYLES`, set their
          style attribute according to :py:data:`~.TAGSTYLES`.

        Elements which have a "jivemacro" attribute present will not be
        modified.

        :param root: root node of etree to jive-ize
        :type root: ``lxml.etree._Element``
        :param no_sourcecode_style: If True, remove the ``style`` attribute from
          any ``div`` elements with a class of ``sourceCode``.
        :type no_sourcecode_style: bool
        :return: root node of etree containing jive-ized HTML
        :rtype: ``lxml.etree._Element`` or ``lxml.etree._ElementTree``
        """
        # sourceCode div cleanup
        if no_sourcecode_style:
            for code_div in root.xpath('//div[@class="sourceCode"]'):
                del code_div.attrib['style']
        # prefix all newlines in <pre> tags with ``<br />``
        for pre in root.xpath('//pre'):
            if 'jivemacro' in pre.attrib:
                continue
            pre.getparent().replace(pre, newline_to_br(pre))
        # ok, now apply some general Fuel/Jive style fixes...
        for element in root.iter():
            if element.tag not in TAGSTYLES.keys():
                continue
            if (
                'jivemacro' in element.attrib or
                'jivemacro' in element.getparent().attrib
            ):
                continue
            element.attrib['style'] = TAGSTYLES[element.tag]
        return root

    @staticmethod
    def _is_local_image(src):
        """
        Given the string path to an image, return True if it appears to be a
        local image and False if it appears to be a remote image. We consider
        an image remote (return False) if :py:func:`urllib.parse.urlparse`
        returns an empty string for ``scheme``, or local (return True)
        otherwise. Also returns False if ``src`` is ``None``.

        :param src: the value of image tag's ``src`` attribute
        :type src: str
        :return: True if the image appears to be local (relative or absolute
          path) or False if it appears to be remote
        :rtype: bool
        """
        if src is None:
            return False
        p = urlparse(src)
        if p.scheme == '':
            return True
        return False

    def _load_image_from_disk(self, img_path):
        """
        Given the path to an image taken from the ``src`` attribute of an
        ``img`` tag, load it from disk. If the path is relative, it will be
        loaded relative to ``self._image_dir``. Return a 3-tuple of a string
        describing the Content-Type of the image, the raw bytes of the image
        data, and the sha256 sum of the image data. The content type is
        determined using the Python standard library's :py:func:`imghdr.what`.

        :param img_path: path to the image on disk
        :type img_path: str
        :return: (``str`` Content-Type, ``bytes`` binary image content read
          from disk, ``str`` hex sha256 sum of ``bytes``)
        :rtype: tuple
        """
        logger.debug('Load image from disk: %s', img_path)
        if not os.path.isabs(img_path):
            img_path = os.path.abspath(os.path.join(self._image_dir, img_path))
            logger.debug('Image absolute path: %s', img_path)
        with open(img_path, 'rb') as fh:
            imgdata = fh.read()
        content_type = 'image/' + imghdr.what(None, imgdata)
        logger.debug(
            'Loaded %d byte image; found content-type as: %s',
            len(imgdata), content_type
        )
        img_sha256 = hashlib.sha256(imgdata).hexdigest()
        return content_type, imgdata, img_sha256

    def _upload_images(self, root, images={}):
        """
        Given the root Element of a (HTML) document, find all ``img`` tags. For
        any of them that have a ``src`` attribute pointing to a local image (as
        determined by :py:meth:`~._is_local_image`), read the corresponding
        image file from disk, upload it to the Jive server, and then replace the
        ``src`` attribute with the upload temporary URL and add an entry to
        the image dictionary (second element of the return value).

        The format of the second element of the return value is the images dict
        format described in this class under
        :ref:`JiveContent Images Dict Format <images-dict-format>`.

        **Important:** The images dict (second element of return value) must be
        externally persisted.

        :param root: root node of etree to inline CSS in
        :type root: ``lxml.etree._Element``
        :return: 2-tuple of (``root`` with attributes modified as appropriate,
          and a dict mapping the original image paths to the API response data
          for them)
        :rtype: tuple
        """
        for img in root.xpath('//img'):
            src = img.get('src')
            if not JiveContent._is_local_image(src):
                logger.debug('Non-local image: %s', src)
                continue
            # if it's local, get the data, content type, and filename
            img_content_type, img_data, img_sha256 = self._load_image_from_disk(
                src
            )
            if img_sha256 in images:
                logger.debug(
                    'Image %s already uploaded per images dict; location=%s '
                    'id=%s (identified via sha256=%s)', src,
                    images[img_sha256]['location'],
                    images[img_sha256]['jive_object']['id'], img_sha256
                )
                img.set('src', images[img_sha256]['location'])
                continue
            logger.debug(
                'Image %s content-type=%s sha256=%s',
                src, img_content_type, img_sha256
            )
            img_fname = os.path.basename(src)
            logger.debug(
                'Uploading Image with filename "%s" and MIME Content-Type '
                '%s from img src="%s"', img_fname, img_content_type, src
            )
            # do the upload and capture response and Location
            img_uri, api_response = self._api.upload_image(
                img_data, img_fname, img_content_type
            )
            logger.debug(
                'Image uploaded for "%s"; id=%s Location=%s', src,
                api_response['id'], img_uri
            )
            # update image state dict
            images[img_sha256] = {
                'location': img_uri,
                'jive_object': api_response,
                'local_path': src
            }
            logger.debug('Rewrite img src from "%s" to "%s"', src, img_uri)
            # set the src attribute to the Location
            img.set('src', img_uri)
        return root, images
