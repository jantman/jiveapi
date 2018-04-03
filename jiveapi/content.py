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
        self, subject, html, tags=[], place_id=None, visibility=None,
        set_datetime=None, inline_css=True, jiveize=True
    ):
        """
        Create a HTML `Document <https://developers.jivesoftware.com/api/v3/clou
        d/rest/DocumentEntity.html>`_ in Jive. This is a convenience wrapper
        around :py:meth:`~.create_content` to assist with forming the content
        JSON, as well as to assist with HTML handling.

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
        :return: representation of the created Document content object
        :rtype: dict
        """
        if jiveize or inline_css:
            doc = JiveContent.html_to_etree(html)
            if inline_css:
                logger.debug('Passing input HTML through inline_css_etree()')
                doc = JiveContent.inline_css_etree(doc)
            if jiveize:
                logger.debug('Passing input HTML through jiveize_etree()')
                doc = JiveContent.jiveize_etree(doc)
            html = etree.tostring(doc)
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
