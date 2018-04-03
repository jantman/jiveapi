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

import logging

from lxml import etree
from premailer import Premailer

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
    :type elem: lxml.etree._Element
    :return: modified element
    :rtype: lxml.etree._Element
    """
    src = etree.tostring(elem).strip()
    if isinstance(src, type(b'')):  # nocoverage
        src = src.decode()
    res = src.replace("\n", "<br/>\n")
    return etree.fromstring(res + "\n")


class JiveContent(object):

    def __init__(self, api):
        """
        Initialize the JiveContent wrapper.

        :param api: authenticated API instance
        :type api: jiveapi.api.JiveApi
        """
        self._api = api

    def create_html_document(
        self, subject, body, tags=[], place_id=None, visibility=None,
        set_datetime=None
    ):
        """
        Create a HTML `Document <https://developers.jivesoftware.com/api/v3/clou
        d/rest/DocumentEntity.html>`_ in Jive. This is a convenience wrapper
        around :py:meth:`~.create_content` to assist with forming the content
        JSON.

        :param subject: The subject / title of the Document.
        :type subject: str
        :param body: The HTML body of the Document. See the notes in the jiveapi
          package documentation about HTML handling.
        :type body: str
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
        :return: representation of the created Document content object
        :rtype: dict
        """
        content = {
            'type': 'document',
            'subject': subject,
            'content': {
                'type': 'text/html',
                'text': body
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
        if set_datetime is not None:
            return self._api.create_content(content, publish_date=set_datetime)
        return self._api.create_content(content)

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
        :type root: lxml.etree._Element
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
        it to render correctly in the Jive UI:

        * If ``no_sourcecode_style`` is True, remove the ``style`` attribute
          from any ``div`` elements with a class of ``sourceCode``.
        * In all ``<pre>`` elements, convert ``\n`` to ``<br />\n`` via
          :py:func:`~.newline_to_br`.
        * For any HTML tags that are keys of :py:const:`~.TAGSTYLES`, set their
          style attribute according to :py:const:`~.TAGSTYLES`.

        :param root: root node of etree to jive-ize
        :type root: lxml.etree._Element
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
            pre.getparent().replace(pre, newline_to_br(pre))
        # ok, now apply some general Fuel/Jive style fixes...
        for element in root.iter():
            if element.tag not in TAGSTYLES.keys():
                continue
            element.attrib['style'] = TAGSTYLES[element.tag]
        return root


"""
## Document with embedded images GET example:

  "content" : {
    "text" : "<body><!-- [DocumentBodyStart:1693a4b1-d031-49cf-89f0-c768af9badbd] --><div class=\"jive-rendered-content\"><p>This is one image&#160;<a href=\"https://<JIVE-HOST>/servlet/JiveServlet/showImage/102-181245-3-601173/20x20.png\"><img alt=\"image description 20x20\" class=\"image-2 jive-image j-img-original\" height=\"20\" src=\"https://<JIVE-HOST>/servlet/JiveServlet/downloadImage/102-181245-3-601173/20x20.png\" style=\"height: auto;\" width=\"20\"/></a> and this is another:&#160;<a href=\"https://<JIVE-HOST>/servlet/JiveServlet/showImage/102-181245-3-601172/25x25.png\"><img alt=\"image description 25x25\" class=\"image-1 jive-image j-img-original\" height=\"25\" src=\"https://<JIVE-HOST>/servlet/JiveServlet/downloadImage/102-181245-3-601172/25x25.png\" style=\"height: auto;\" width=\"25\"/></a></p></div><!-- [DocumentBodyEnd:1693a4b1-d031-49cf-89f0-c768af9badbd] --></body>",
    "editable" : false,
    "type" : "text/html"
  },
  "contentImages" : [ {
    "id" : "601172",
    "ref" : "https://<JIVE-HOST>/api/core/v3/images/601172?a=1522455592480",
    "size" : 167,
    "width" : 25,
    "height" : 25,
    "type" : "image",
    "typeCode" : 111
  }, {
    "id" : "601173",
    "ref" : "https://<JIVE-HOST>/api/core/v3/images/601173?a=1522455592433",
    "size" : 165,
    "width" : 20,
    "height" : 20,
    "type" : "image",
    "typeCode" : 111
  } ],
  "attachments" : [ ],

## Adding Embedded Images to Content:
https://community.jivesoftware.com/docs/DOC-233174#jive_content_id_Adding_Embedded_Images_to_a_Piece_of_Content

1. Upload Image (POST multipart/form-data) See: Images Service
2. Read Location HTTP Header for API URI for Image
3. Add HTML Markup in Content Body using the new API URI for the Image, see: Contents Service > Update Content
  * May find value in the Contents Service > Update Editable Content if you want to leverage RTE macros.
    * Note the documentation callout : The input JSON must include a true value in content.editable if the content body is using RTE macros.

## Creating and Updating content with embedded images:

So here's my theory:

* When we create, the method should return a dict with a "contentID" key and an
"images" key. Those both need to be stored by the caller. The "images" key will
contain a mapping from image filenames (src attribute in the original HTML) to
a dict of the Jive imageID / API URL and the Jive user-facing URL (both of which
are returned by ``api.upload_image()``.
* When we want to update, we'll have to pass back in the contentID, the new HTML,
and that images dict. We'll then need to GET the existing content object in Jive.
Once we have the existing content object, we can examine its ``contentImages``
key to see what images it has. We'll have to download each of them locally via
their ``ref`` key and do a binary comparison on the local images to determine if
we should use an existing image or upload a new one.

So we GET the existing content from Jive, pull a list of the image (local) paths
in the input HTML, and also have an ``images`` dict that was stored from the
original content creation. For each of the local image paths in the HTML:

1. If it's not in the persisted ``images`` dict, upload the new image and replace
the local path in the HTML with the uploaded path. Update ``images`` dict with
the new information. Move on to next.
2. GET the actual binary image that's persisted for it in the ``images`` dict
and compare the two binary images.
3. If the images differ, then we need to upload a new one. Remove the current
entry from the ``images`` dict and jump back to #1.
4. Finally, we have an unchanged image. Unfortunately this is difficult. When
images are initially uploaded (e.g. #1, above) they're given a temporary API-
based URL that we put in the HTML. But once the HTML is uploaded and processed,
the images are given a permanent client-facing URL, like
``https://sandbox.jiveon.com/servlet/JiveServlet/downloadImage/102-181245-3-601173/20x20.png``. We'll need to build this URL ourselves, and then replace the local
image path in our HTML with this persistent image (so that we show the same
image that was there previously). One way to do this would be to GET newly
created or uploaded Content objects right after we upload them, and find the new
client-facing URLs for the images. But there's a programmatic way to do it.

Let's take this example URL:
https://sandbox.jiveon.com/servlet/JiveServlet/downloadImage/102-181245-3-601173/20x20.png

That image was originally uploaded (via ``api.upload_image()`` with a filename
of ``20x20.png``, and that upload generated an Image with ID 601173. The image
is attached to a Document whose API object representation includes, in part:

{
  "entityType" : "document",
  "id" : "181245",
  "content" : {
    "text" : "<body><!-- [DocumentBodyStart:1693a4b1-d031-49cf-89f0-c768af9badbd] --><div class=\"jive-rendered-content\"><p>This is one image&#160;<a href=\"https://sandbox.jiveon.com/servlet/JiveServlet/showImage/102-181245-3-601173/20x20.png\"><img alt=\"image description 20x20\" class=\"image-2 jive-image j-img-original\" height=\"20\" src=\"https://sandbox.jiveon.com/servlet/JiveServlet/downloadImage/102-181245-3-601173/20x20.png\" style=\"height: auto;\" width=\"20\"/></a> and this is another:&#160;<a href=\"https://sandbox.jiveon.com/servlet/JiveServlet/showImage/102-181245-3-601172/25x25.png\"><img alt=\"image description 25x25\" class=\"image-1 jive-image j-img-original\" height=\"25\" src=\"https://sandbox.jiveon.com/servlet/JiveServlet/downloadImage/102-181245-3-601172/25x25.png\" style=\"height: auto;\" width=\"25\"/></a></p></div><!-- [DocumentBodyEnd:1693a4b1-d031-49cf-89f0-c768af9badbd] --></body>",
    "editable" : false,
    "type" : "text/html"
  },
  "contentImages" : [ {
    "id" : "601173",
    "ref" : "https://sandbox.jiveon.com/api/core/v3/images/601173?a=1522455592433",
    "size" : 165,
    "width" : 20,
    "height" : 20,
    "type" : "image",
    "typeCode" : 111
  } ],
  "version" : 3,
  "type" : "document",
  "typeCode" : 102
} 

So we see that the path of:

``/servlet/JiveServlet/downloadImage/102-181245-3-601173/20x20.png``

appears to have a fixed prefix of ``/servlet/JiveServlet/downloadImage/``
followed by
``<typeCode>-<id>-<version>-<Image ID>/<upload filename>``

At the end of this, we'll need to make sure we pruned any stale entries from
our ``images`` dict before we return it back to the caller.

## Stuff about Editable Content and RTE Macros
https://developers.jivesoftware.com/api/v3/cloud/rest/ContentService.html#updateEditableContent(String, String, boolean, boolean, String)

## Table of Contents macro:
replace(
    '<!--- INSERT TABLE OF CONTENTS HERE -->',
    '<p style="color: #24292e; margin-top: 0; margin-bottom: 16px;"><img '
    'alt="Table of contents" class="jive_macro jive_macro_toc" src="/images/'
    'tiny_mce4/themes/advanced/img/toc.png" jivemacro="toc" /></p>'
)

## Performance Note:
see https://community.jivesoftware.com/docs/DOC-233174#jive_content_id_Suppressing_Fields_from_API_Responses

"""
