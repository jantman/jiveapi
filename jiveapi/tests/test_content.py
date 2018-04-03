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
from datetime import datetime
from urllib.parse import urljoin
from unittest.mock import Mock, call, patch

from lxml import etree
from lxml.html import builder as E

from jiveapi.content import JiveContent, newline_to_br
from jiveapi.api import JiveApi
from jiveapi.tests.test_helpers import FixedOffset
from jiveapi.version import VERSION, PROJECT_URL

pbm = 'jiveapi.content'
pb = '%s.JiveContent' % pbm


class TestInit(object):

    def test_init(self):
        m_api = Mock()
        cls = JiveContent(m_api)
        assert cls._api == m_api


class TestNewlineToBr(object):

    def test_newline_to_br(self):
        mock_html = E.HTML(
            E.HEAD(E.TITLE('Some Title')),
            E.BODY(E.P('Hello\nGoodbye'))
        )
        elem = mock_html.getroottree().xpath('//p')[0]
        assert etree.tostring(elem) == b'<p>Hello\nGoodbye</p>'
        res = newline_to_br(elem)
        assert etree.tostring(res) == b'<p>Hello<br/>\nGoodbye</p>'


class ContentTester(object):

    def setup(self):

        def se_abs_url(p):
            return urljoin('http://jive.example.com/api/', p)

        self.mockapi = Mock(spec_set=JiveApi)
        self.mockapi.abs_url.side_effect = se_abs_url
        self.cls = JiveContent(self.mockapi)


class TestCreateHtmlDocument(ContentTester):

    def test_defaults(self):
        rval = Mock()
        self.mockapi.create_content.return_value = rval
        res = self.cls.create_html_document('subj', 'body')
        assert res == rval
        assert self.mockapi.mock_calls == [
            call.create_content({
                'type': 'document',
                'subject': 'subj',
                'content': {
                    'type': 'text/html',
                    'text': 'body'
                },
                'via': {
                    'displayName': 'Python jiveapi v%s' % VERSION,
                    'url': PROJECT_URL
                }
            })
        ]

    def test_tags(self):
        rval = Mock()
        self.mockapi.create_content.return_value = rval
        res = self.cls.create_html_document(
            'subj', 'body', tags=['foo', 'bar', 'baz']
        )
        assert res == rval
        assert self.mockapi.mock_calls == [
            call.create_content({
                'type': 'document',
                'subject': 'subj',
                'content': {
                    'type': 'text/html',
                    'text': 'body'
                },
                'tags': ['foo', 'bar', 'baz'],
                'via': {
                    'displayName': 'Python jiveapi v%s' % VERSION,
                    'url': PROJECT_URL
                }
            })
        ]

    def test_place(self):
        rval = Mock()
        self.mockapi.create_content.return_value = rval
        res = self.cls.create_html_document(
            'subj', 'body', place_id='12345'
        )
        assert res == rval
        assert self.mockapi.mock_calls == [
            call.abs_url('core/v3/places/12345'),
            call.create_content({
                'type': 'document',
                'subject': 'subj',
                'content': {
                    'type': 'text/html',
                    'text': 'body'
                },
                'parent': 'http://jive.example.com/api/core/v3/places/12345',
                'via': {
                    'displayName': 'Python jiveapi v%s' % VERSION,
                    'url': PROJECT_URL
                }
            })
        ]

    def test_visibility(self):
        rval = Mock()
        self.mockapi.create_content.return_value = rval
        res = self.cls.create_html_document(
            'subj', 'body', visibility='hidden'
        )
        assert res == rval
        assert self.mockapi.mock_calls == [
            call.create_content({
                'type': 'document',
                'subject': 'subj',
                'content': {
                    'type': 'text/html',
                    'text': 'body'
                },
                'visibility': 'hidden',
                'via': {
                    'displayName': 'Python jiveapi v%s' % VERSION,
                    'url': PROJECT_URL
                }
            })
        ]

    def test_publish_date(self):
        rval = Mock()
        self.mockapi.create_content.return_value = rval
        dt = datetime(2018, 2, 13, 11, 52, 18, tzinfo=FixedOffset(-60, 'foo'))
        res = self.cls.create_html_document(
            'subj', 'body', visibility='hidden', set_datetime=dt
        )
        assert res == rval
        assert self.mockapi.mock_calls == [
            call.create_content({
                'type': 'document',
                'subject': 'subj',
                'content': {
                    'type': 'text/html',
                    'text': 'body'
                },
                'visibility': 'hidden',
                'via': {
                    'displayName': 'Python jiveapi v%s' % VERSION,
                    'url': PROJECT_URL
                }
            }, publish_date=dt)
        ]


class TestHtmlToEtree(object):

    def test_without_doctype(self):
        html_in = '<html><head><title>Title</title><style type="text/css">' \
                  'h1, h2 { color:red; }' \
                  'strong { text-decoration:none; }' \
                  '</style></head><body><h1>Hi!</h1><p><strong>Yes!</strong>' \
                  '</p></body></html>'
        res = JiveContent.html_to_etree(html_in)
        assert isinstance(res, etree._Element)
        assert hasattr(res, 'docinfo') is False
        assert etree.tostring(res) == html_in.encode('utf-8')

    def test_with_doctype(self):
        html_in = '<!DOCTYPE html>\n' \
                  '<html xmlns="http://www.w3.org/1999/xhtml" lang="" ' \
                  'xml:lang="">' \
                  '<head><title>Title</title><style type="text/css">' \
                  'h1, h2 { color:red; }' \
                  'strong { text-decoration:none; }' \
                  '</style></head><body><h1>Hi!</h1><p><strong>Yes!</strong>' \
                  '</p></body></html>'
        expected = '<html xmlns="http://www.w3.org/1999/xhtml" lang="" ' \
                   'xml:lang="">' \
                   '<head><title>Title</title><style type="text/css">' \
                   'h1, h2 { color:red; }' \
                   'strong { text-decoration:none; }' \
                   '</style></head><body><h1>Hi!</h1><p><strong>Yes!</strong>' \
                   '</p></body></html>'
        res = JiveContent.html_to_etree(html_in)
        assert isinstance(res, etree._Element)
        assert hasattr(res, 'docinfo') is False
        assert etree.tostring(res) == expected.encode('utf-8')


class TestInlineCssHtml(object):

    def test_inline_css_html(self):
        m_ice = Mock()
        m_hte = Mock()
        with patch('%s.inline_css_etree' % pb) as mock_ice:
            with patch('%s.html_to_etree' % pb) as mock_hte:
                with patch('%s.etree.tostring' % pbm) as mock_ets:
                    mock_ice.return_value = m_ice
                    mock_hte.return_value = m_hte
                    mock_ets.return_value = 'someString'
                    res = JiveContent.inline_css_html('HTMLin')
        assert res == 'someString'
        assert mock_hte.mock_calls == [call('HTMLin')]
        assert mock_ice.mock_calls == [call(m_hte)]
        assert mock_ets.mock_calls == [call(m_ice)]


class TestInlineCssEtree(object):

    def test_inline_css_etree(self):
        mock_root = Mock()
        mock_res = Mock()
        with patch('%s.Premailer' % pbm, create=True) as mock_premailer:
            mock_premailer.return_value.transform.return_value = mock_res
            res = JiveContent.inline_css_etree(mock_root)
        assert res == mock_res
        assert mock_premailer.mock_calls == [
            call(mock_root),
            call().transform()
        ]


class TestJiveizeHtml(object):

    def test_no_sourcecode_true(self):
        m_je = Mock()
        m_hte = Mock()
        with patch('%s.jiveize_etree' % pb) as mock_je:
            with patch('%s.html_to_etree' % pb) as mock_hte:
                with patch('%s.etree.tostring' % pbm) as mock_ets:
                    mock_je.return_value = m_je
                    mock_hte.return_value = m_hte
                    mock_ets.return_value = 'someString'
                    res = JiveContent.jiveize_html('HTMLin')
        assert res == 'someString'
        assert mock_hte.mock_calls == [call('HTMLin')]
        assert mock_je.mock_calls == [
            call(m_hte, no_sourcecode_style=True)
        ]
        assert mock_ets.mock_calls == [call(m_je)]

    def test_no_sourcecode_false(self):
        m_je = Mock()
        m_hte = Mock()
        with patch('%s.jiveize_etree' % pb) as mock_je:
            with patch('%s.html_to_etree' % pb) as mock_hte:
                with patch('%s.etree.tostring' % pbm) as mock_ets:
                    mock_je.return_value = m_je
                    mock_hte.return_value = m_hte
                    mock_ets.return_value = 'someString'
                    res = JiveContent.jiveize_html(
                        'HTMLin', no_sourcecode_style=False
                    )
        assert res == 'someString'
        assert mock_hte.mock_calls == [call('HTMLin')]
        assert mock_je.mock_calls == [
            call(m_hte, no_sourcecode_style=False)
        ]
        assert mock_ets.mock_calls == [call(m_je)]


class TestHtmlAcceptance(object):

    def test_example(self, fixtures_path):
        in_path = os.path.join(fixtures_path, 'html', 'testpostA.html')
        out_path = os.path.join(
            fixtures_path, 'html', 'testpostA.jive_and_inline.html'
        )
        with open(in_path, 'r') as fh:
            in_html = fh.read()
        with open(out_path, 'r') as fh:
            expected = fh.read()
        tree = JiveContent.html_to_etree(in_html)
        res = JiveContent.jiveize_etree(
            JiveContent.inline_css_etree(tree)
        )
        assert etree.tostring(res).decode() == expected

    def test_example_no_sourcecode_style(self, fixtures_path):
        in_path = os.path.join(fixtures_path, 'html', 'testpostA.html')
        out_path = os.path.join(
            fixtures_path, 'html', 'testpostA.jive_and_inline.nosrc.html'
        )
        with open(in_path, 'r') as fh:
            in_html = fh.read()
        with open(out_path, 'r') as fh:
            expected = fh.read()
        tree = JiveContent.html_to_etree(in_html)
        res = JiveContent.jiveize_etree(
            JiveContent.inline_css_etree(tree),
            no_sourcecode_style=False
        )
        assert etree.tostring(res).decode() == expected
