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
from unittest.mock import Mock, call, patch, DEFAULT, mock_open

from lxml import etree
from lxml.html import builder as E

from jiveapi.content import JiveContent, newline_to_br
from jiveapi.api import JiveApi
from jiveapi.tests.test_helpers import FixedOffset
from jiveapi.version import VERSION, PROJECT_URL

pbm = 'jiveapi.content'
pb = '%s.JiveContent' % pbm
sha256str = '9f862d5353358cb5993685c00f3e315496d26f5db2659e07e1665aa09896657e'


class TestInit(object):

    def test_init(self):
        m_api = Mock()
        with patch('%s.os.getcwd' % pbm) as mock_getcwd:
            mock_getcwd.return_value = '/my/cwd'
            cls = JiveContent(m_api)
        assert cls._api == m_api
        assert cls._image_dir == '/my/cwd'

    def test_init_image_dir(self):
        m_api = Mock()
        with patch('%s.os.getcwd' % pbm) as mock_getcwd:
            mock_getcwd.return_value = '/my/cwd'
            cls = JiveContent(m_api, image_dir='/foo/bar')
        assert cls._api == m_api
        assert cls._image_dir == '/foo/bar'


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
        self.cls = JiveContent(self.mockapi, image_dir='/img/dir')

    def example_doc(self):
        return {
            'entityType': 'docment',
            'id': '12345',
            'resources': {
                'editHtml': {
                    'allowed': ['GET', 'PUT'],
                    'ref': 'http://jive.example.com/docs/DOC-12345/edit'
                },
                'html': {
                    'allowed': ['GET'],
                    'ref': 'http://jive.example.com/docs/DOC-12345'
                }
            },
            'contentID': '6789',
            'content': {
                'text': '<p>Some Html</p>',
                'editable': False,
                'type': 'text/html'
            },
            'status': 'published',
            'subject': 'My Subject',
            'type': 'docment',
            'typeCode': 102
        }


class TestCreateHtmlDocument(ContentTester):

    def test_defaults(self):
        self.mockapi.create_content.return_value = self.example_doc()
        with patch('%s.dict_for_html_document' % pb) as mock_dfhd:
            mock_dfhd.return_value = ({'foo': 'bar'}, {'images': 'foo'})
            res = self.cls.create_html_document('subj', 'body')
        assert res == {
            'entityType': 'docment',
            'id': '12345',
            'html_ref': 'http://jive.example.com/docs/DOC-12345',
            'contentID': '6789',
            'type': 'docment',
            'typeCode': 102,
            'images': {'images': 'foo'}
        }
        assert self.mockapi.mock_calls == [
            call.create_content({'foo': 'bar'})
        ]
        assert mock_dfhd.mock_calls == [
            call(
                'subj', 'body', tags=[], place_id=None, visibility=None,
                inline_css=True, jiveize=True, handle_images=True
            )
        ]

    def test_non_defaults(self):
        dt = datetime(2018, 2, 13, 11, 52, 18, tzinfo=FixedOffset(-60, 'foo'))
        self.mockapi.create_content.return_value = self.example_doc()
        with patch('%s.dict_for_html_document' % pb) as mock_dfhd:
            mock_dfhd.return_value = ({'foo': 'bar'}, {'images': 'foo'})
            res = self.cls.create_html_document(
                'subj', 'body', tags=['foo'], place_id='1234',
                visibility='place', set_datetime=dt, inline_css=False,
                jiveize=False, handle_images=False
            )
        assert res == {
            'entityType': 'docment',
            'id': '12345',
            'html_ref': 'http://jive.example.com/docs/DOC-12345',
            'contentID': '6789',
            'type': 'docment',
            'typeCode': 102,
            'images': {'images': 'foo'}
        }
        assert self.mockapi.mock_calls == [
            call.create_content({'foo': 'bar'}, publish_date=dt)
        ]
        assert mock_dfhd.mock_calls == [
            call(
                'subj', 'body', tags=['foo'], place_id='1234',
                visibility='place', inline_css=False, jiveize=False,
                handle_images=False
            )
        ]


class TestUpdateHtmlDocument(ContentTester):

    def test_defaults(self):
        self.mockapi.update_content.return_value = self.example_doc()
        with patch('%s.dict_for_html_document' % pb) as mock_dfhd:
            mock_dfhd.return_value = ({'foo': 'bar'}, {'images': 'foo'})
            res = self.cls.update_html_document('6789', 'subj', 'body')
        assert res == {
            'entityType': 'docment',
            'id': '12345',
            'html_ref': 'http://jive.example.com/docs/DOC-12345',
            'contentID': '6789',
            'type': 'docment',
            'typeCode': 102,
            'images': {'images': 'foo'}
        }
        assert self.mockapi.mock_calls == [
            call.update_content('6789', {'foo': 'bar'})
        ]
        assert mock_dfhd.mock_calls == [
            call(
                'subj', 'body', tags=[], place_id=None, visibility=None,
                inline_css=True, jiveize=True, handle_images=True, images={}
            )
        ]

    def test_non_defaults(self):
        dt = datetime(2018, 2, 13, 11, 52, 18, tzinfo=FixedOffset(-60, 'foo'))
        self.mockapi.update_content.return_value = self.example_doc()
        with patch('%s.dict_for_html_document' % pb) as mock_dfhd:
            mock_dfhd.return_value = ({'foo': 'bar'}, {'images': 'foo'})
            res = self.cls.update_html_document(
                '6789', 'subj', 'body', tags=['foo'], place_id='1234',
                visibility='place', set_datetime=dt, inline_css=False,
                jiveize=False, handle_images=False, images={'input': 'bar'}
            )
        assert res == {
            'entityType': 'docment',
            'id': '12345',
            'html_ref': 'http://jive.example.com/docs/DOC-12345',
            'contentID': '6789',
            'type': 'docment',
            'typeCode': 102,
            'images': {'images': 'foo'}
        }
        assert self.mockapi.mock_calls == [
            call.update_content('6789', {'foo': 'bar'}, update_date=dt)
        ]
        assert mock_dfhd.mock_calls == [
            call(
                'subj', 'body', tags=['foo'], place_id='1234',
                visibility='place', inline_css=False, jiveize=False,
                handle_images=False, images={'input': 'bar'}
            )
        ]


class TestDictForHtmlDocument(ContentTester):

    def test_defaults_with_images(self):
        m_hte = Mock()
        m_ice = Mock()
        m_je = Mock()
        m_ui = Mock()
        with patch.multiple(
            pb,
            html_to_etree=DEFAULT,
            inline_css_etree=DEFAULT,
            jiveize_etree=DEFAULT,
            _upload_images=DEFAULT
        ) as mocks:
            with patch('%s.etree.tostring' % pbm) as mock_tostring:
                mock_tostring.return_value = 'fixed_string'
                mocks['html_to_etree'].return_value = m_hte
                mocks['inline_css_etree'].return_value = m_ice
                mocks['jiveize_etree'].return_value = m_je
                mocks['_upload_images'].return_value = m_ui, {'images': 'foo'}
                res = self.cls.dict_for_html_document(
                    'subj', 'body', images={'input': 'images'}
                )
        assert res == ({
            'type': 'document',
            'subject': 'subj',
            'content': {
                'type': 'text/html',
                'text': 'fixed_string'
            },
            'via': {
                'displayName': 'Python jiveapi v%s' % VERSION,
                'url': PROJECT_URL
            }
        }, {'images': 'foo'})
        assert mocks['html_to_etree'].mock_calls == [call('body')]
        assert mocks['inline_css_etree'].mock_calls == [call(m_hte)]
        assert mocks['jiveize_etree'].mock_calls == [call(m_ice)]
        assert mocks['_upload_images'].mock_calls == [
            call(m_je, {'input': 'images'})
        ]
        assert mock_tostring.mock_calls == [call(m_ui)]
        assert self.mockapi.mock_calls == []

    def test_no_modify(self):
        m_hte = Mock()
        m_ice = Mock()
        m_je = Mock()
        m_ui = Mock()
        with patch.multiple(
            pb,
            html_to_etree=DEFAULT,
            inline_css_etree=DEFAULT,
            jiveize_etree=DEFAULT,
            _upload_images=DEFAULT
        ) as mocks:
            with patch('%s.etree.tostring' % pbm) as mock_tostring:
                mock_tostring.return_value = 'fixed_string'
                mocks['html_to_etree'].return_value = m_hte
                mocks['inline_css_etree'].return_value = m_ice
                mocks['jiveize_etree'].return_value = m_je
                mocks['_upload_images'].return_value = m_ui, {'images': 'foo'}
                res = self.cls.dict_for_html_document(
                    'subj', 'body', jiveize=False, inline_css=False,
                    handle_images=False
                )
        assert res == ({
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
        }, {})
        assert mocks['html_to_etree'].mock_calls == []
        assert mocks['inline_css_etree'].mock_calls == []
        assert mocks['jiveize_etree'].mock_calls == []
        assert mocks['_upload_images'].mock_calls == []
        assert mock_tostring.mock_calls == []
        assert self.mockapi.mock_calls == []

    def test_no_jiveize(self):
        m_hte = Mock()
        m_ice = Mock()
        m_je = Mock()
        m_ui = Mock()
        with patch.multiple(
            pb,
            html_to_etree=DEFAULT,
            inline_css_etree=DEFAULT,
            jiveize_etree=DEFAULT,
            _upload_images=DEFAULT
        ) as mocks:
            with patch('%s.etree.tostring' % pbm) as mock_tostring:
                mock_tostring.return_value = 'fixed_string'
                mocks['html_to_etree'].return_value = m_hte
                mocks['inline_css_etree'].return_value = m_ice
                mocks['jiveize_etree'].return_value = m_je
                mocks['_upload_images'].return_value = m_ui, {'images': 'foo'}
                res = self.cls.dict_for_html_document(
                    'subj', 'body', jiveize=False
                )
        assert res == ({
            'type': 'document',
            'subject': 'subj',
            'content': {
                'type': 'text/html',
                'text': 'fixed_string'
            },
            'via': {
                'displayName': 'Python jiveapi v%s' % VERSION,
                'url': PROJECT_URL
            }
        }, {'images': 'foo'})
        assert mocks['html_to_etree'].mock_calls == [call('body')]
        assert mocks['inline_css_etree'].mock_calls == [call(m_hte)]
        assert mocks['jiveize_etree'].mock_calls == []
        assert mocks['_upload_images'].mock_calls == [call(m_ice, {})]
        assert mock_tostring.mock_calls == [call(m_ui)]
        assert self.mockapi.mock_calls == []

    def test_no_inline(self):
        m_hte = Mock()
        m_ice = Mock()
        m_je = Mock()
        m_ui = Mock()
        with patch.multiple(
            pb,
            html_to_etree=DEFAULT,
            inline_css_etree=DEFAULT,
            jiveize_etree=DEFAULT,
            _upload_images=DEFAULT
        ) as mocks:
            with patch('%s.etree.tostring' % pbm) as mock_tostring:
                mock_tostring.return_value = 'fixed_string'
                mocks['html_to_etree'].return_value = m_hte
                mocks['inline_css_etree'].return_value = m_ice
                mocks['jiveize_etree'].return_value = m_je
                mocks['_upload_images'].return_value = m_ui, {'images': 'foo'}
                res = self.cls.dict_for_html_document(
                    'subj', 'body', inline_css=False
                )
        assert res == ({
            'type': 'document',
            'subject': 'subj',
            'content': {
                'type': 'text/html',
                'text': 'fixed_string'
            },
            'via': {
                'displayName': 'Python jiveapi v%s' % VERSION,
                'url': PROJECT_URL
            }
        }, {'images': 'foo'})
        assert mocks['html_to_etree'].mock_calls == [call('body')]
        assert mocks['inline_css_etree'].mock_calls == []
        assert mocks['jiveize_etree'].mock_calls == [call(m_hte)]
        assert mocks['_upload_images'].mock_calls == [call(m_je, {})]
        assert mock_tostring.mock_calls == [call(m_ui)]
        assert self.mockapi.mock_calls == []

    def test_no_images(self):
        m_hte = Mock()
        m_ice = Mock()
        m_je = Mock()
        m_ui = Mock()
        with patch.multiple(
            pb,
            html_to_etree=DEFAULT,
            inline_css_etree=DEFAULT,
            jiveize_etree=DEFAULT,
            _upload_images=DEFAULT
        ) as mocks:
            with patch('%s.etree.tostring' % pbm) as mock_tostring:
                mock_tostring.return_value = 'fixed_string'
                mocks['html_to_etree'].return_value = m_hte
                mocks['inline_css_etree'].return_value = m_ice
                mocks['jiveize_etree'].return_value = m_je
                mocks['_upload_images'].return_value = m_ui, {'images': 'foo'}
                res = self.cls.dict_for_html_document(
                    'subj', 'body', handle_images=False
                )
        assert res == ({
            'type': 'document',
            'subject': 'subj',
            'content': {
                'type': 'text/html',
                'text': 'fixed_string'
            },
            'via': {
                'displayName': 'Python jiveapi v%s' % VERSION,
                'url': PROJECT_URL
            }
        }, {})
        assert mocks['html_to_etree'].mock_calls == [call('body')]
        assert mocks['inline_css_etree'].mock_calls == [call(m_hte)]
        assert mocks['jiveize_etree'].mock_calls == [call(m_ice)]
        assert mocks['_upload_images'].mock_calls == []
        assert mock_tostring.mock_calls == [call(m_je)]
        assert self.mockapi.mock_calls == []

    def test_tags(self):
        m_hte = Mock()
        m_ice = Mock()
        m_je = Mock()
        m_ui = Mock()
        with patch.multiple(
            pb,
            html_to_etree=DEFAULT,
            inline_css_etree=DEFAULT,
            jiveize_etree=DEFAULT,
            _upload_images=DEFAULT
        ) as mocks:
            with patch('%s.etree.tostring' % pbm) as mock_tostring:
                mock_tostring.return_value = b'fixed_string'
                mocks['html_to_etree'].return_value = m_hte
                mocks['inline_css_etree'].return_value = m_ice
                mocks['jiveize_etree'].return_value = m_je
                mocks['_upload_images'].return_value = m_ui, {'images': 'foo'}
                res = self.cls.dict_for_html_document(
                    'subj', 'body', tags=['foo', 'bar', 'baz']
                )
        assert res == ({
            'type': 'document',
            'subject': 'subj',
            'content': {
                'type': 'text/html',
                'text': 'fixed_string'
            },
            'tags': ['foo', 'bar', 'baz'],
            'via': {
                'displayName': 'Python jiveapi v%s' % VERSION,
                'url': PROJECT_URL
            }
        }, {'images': 'foo'})
        assert self.mockapi.mock_calls == []

    def test_place(self):
        m_hte = Mock()
        m_ice = Mock()
        m_je = Mock()
        m_ui = Mock()
        with patch.multiple(
            pb,
            html_to_etree=DEFAULT,
            inline_css_etree=DEFAULT,
            jiveize_etree=DEFAULT,
            _upload_images=DEFAULT
        ) as mocks:
            with patch('%s.etree.tostring' % pbm) as mock_tostring:
                mock_tostring.return_value = 'fixed_string'
                mocks['html_to_etree'].return_value = m_hte
                mocks['inline_css_etree'].return_value = m_ice
                mocks['jiveize_etree'].return_value = m_je
                mocks['_upload_images'].return_value = m_ui, {'images': 'foo'}
                res = self.cls.dict_for_html_document(
                    'subj', 'body', place_id='12345'
                )
        assert res == ({
            'type': 'document',
            'subject': 'subj',
            'content': {
                'type': 'text/html',
                'text': 'fixed_string'
            },
            'parent': 'http://jive.example.com/api/core/v3/places/12345',
            'via': {
                'displayName': 'Python jiveapi v%s' % VERSION,
                'url': PROJECT_URL
            }
        }, {'images': 'foo'})
        assert self.mockapi.mock_calls == [
            call.abs_url('core/v3/places/12345')
        ]

    def test_visibility(self):
        m_hte = Mock()
        m_ice = Mock()
        m_je = Mock()
        m_ui = Mock()
        with patch.multiple(
            pb,
            html_to_etree=DEFAULT,
            inline_css_etree=DEFAULT,
            jiveize_etree=DEFAULT,
            _upload_images=DEFAULT
        ) as mocks:
            with patch('%s.etree.tostring' % pbm) as mock_tostring:
                mock_tostring.return_value = 'fixed_string'
                mocks['html_to_etree'].return_value = m_hte
                mocks['inline_css_etree'].return_value = m_ice
                mocks['jiveize_etree'].return_value = m_je
                mocks['_upload_images'].return_value = m_ui, {'images': 'foo'}
                res = self.cls.dict_for_html_document(
                    'subj', 'body', visibility='hidden'
                )
        assert res == ({
            'type': 'document',
            'subject': 'subj',
            'content': {
                'type': 'text/html',
                'text': 'fixed_string'
            },
            'visibility': 'hidden',
            'via': {
                'displayName': 'Python jiveapi v%s' % VERSION,
                'url': PROJECT_URL
            }
        }, {'images': 'foo'})
        assert self.mockapi.mock_calls == []


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


class TestIsLocalImage(object):

    def test_none(self):
        assert JiveContent._is_local_image(None) is False

    def test_http(self):
        assert JiveContent._is_local_image(
            'http://www.example.com/foo.png'
        ) is False

    def test_https(self):
        assert JiveContent._is_local_image(
            'https://www.example.com/foo.png'
        ) is False

    def test_ftp(self):
        assert JiveContent._is_local_image(
            'ftp://www.example.com/foo.png'
        ) is False

    def test_absolute_path(self):
        assert JiveContent._is_local_image(
            '/images/bar/foo.png'
        ) is True

    def test_hostname_absolute_path(self):
        assert JiveContent._is_local_image(
            '/www.example.com/images/foo.png'
        ) is True

    def test_relative_path(self):
        assert JiveContent._is_local_image(
            'bar/foo.png'
        ) is True

    def test_hostname_relative_path(self):
        assert JiveContent._is_local_image(
            'www.example.com/images/foo.png'
        ) is True


class TestLoadImageFromDisk(ContentTester):

    def test_rel_path(self):
        m_sha256 = Mock()
        m_sha256.hexdigest.return_value = sha256str
        with patch('%s.imghdr.what' % pbm) as mock_what:
            with patch('%s.hashlib.sha256' % pbm) as mock_sha256:
                with patch(
                    '%s.open' % pbm, mock_open(read_data=b'foo')
                ) as m_open:
                    mock_what.return_value = 'cType'
                    mock_sha256.return_value = m_sha256
                    res = self.cls._load_image_from_disk('foo/bar.png')
        assert res == ('image/cType', b'foo', sha256str)
        assert mock_what.mock_calls == [call(None, b'foo')]
        assert mock_sha256.mock_calls == [
            call(b'foo'), call().hexdigest()
        ]
        assert m_open.mock_calls == [
            call('/img/dir/foo/bar.png', 'rb'),
            call().__enter__(),
            call().read(),
            call().__exit__(None, None, None)
        ]

    def test_abs_path(self):
        m_sha256 = Mock()
        m_sha256.hexdigest.return_value = sha256str
        with patch('%s.imghdr.what' % pbm) as mock_what:
            with patch('%s.hashlib.sha256' % pbm) as mock_sha256:
                with patch(
                    '%s.open' % pbm, mock_open(read_data=b'foo')
                ) as m_open:
                    mock_what.return_value = 'cType'
                    mock_sha256.return_value = m_sha256
                    res = self.cls._load_image_from_disk('/foo/bar.png')
        assert res == ('image/cType', b'foo', sha256str)
        assert mock_what.mock_calls == [call(None, b'foo')]
        assert mock_sha256.mock_calls == [
            call(b'foo'), call().hexdigest()
        ]
        assert m_open.mock_calls == [
            call('/foo/bar.png', 'rb'),
            call().__enter__(),
            call().read(),
            call().__exit__(None, None, None)
        ]


class TestUploadImages(ContentTester):

    def test_remote_img(self):
        mock_html = E.HTML(
            E.HEAD(E.TITLE('Some Title')),
            E.BODY(
                E.P('Hello\nGoodbye'),
                E.IMG(src='http://example.com/local/img.png')
            )
        )
        root = mock_html.getroottree()
        self.mockapi.upload_image.return_value = (None, None)
        with patch('%s._is_local_image' % pb) as mock_ili:
            with patch('%s._load_image_from_disk' % pb) as mock_lifd:
                mock_ili.return_value = False
                mock_lifd.return_value = (None, None, None)
                newroot, res = self.cls._upload_images(
                    root, images={'foo': {'bar': 'baz'}}
                )
        assert newroot == root
        imgs = newroot.xpath('//img')
        assert len(imgs) == 1
        assert imgs[0].get('src') == 'http://example.com/local/img.png'
        assert res == {'foo': {'bar': 'baz'}}
        assert mock_ili.mock_calls == [
            call('http://example.com/local/img.png')
        ]
        assert mock_lifd.mock_calls == []
        assert self.mockapi.mock_calls == []

    def test_local_new_img(self):
        mock_html = E.HTML(
            E.HEAD(E.TITLE('Some Title')),
            E.BODY(
                E.P('Hello\nGoodbye'),
                E.IMG(src='local/img.png')
            )
        )
        root = mock_html.getroottree()
        self.mockapi.upload_image.return_value = (
            'http://jive.example.com/myimage',
            {'id': '123abc', 'jive': 'imageObject'}
        )
        with patch('%s._is_local_image' % pb) as mock_ili:
            with patch('%s._load_image_from_disk' % pb) as mock_lifd:
                mock_ili.return_value = True
                mock_lifd.return_value = (
                    'image/png', b'imgdata', sha256str
                )
                newroot, res = self.cls._upload_images(root)
        imgs = newroot.xpath('//img')
        assert len(imgs) == 1
        assert imgs[0].get('src') == 'http://jive.example.com/myimage'
        assert res == {
            sha256str: {
                'location': 'http://jive.example.com/myimage',
                'jive_object': {'id': '123abc', 'jive': 'imageObject'},
                'local_path': 'local/img.png'
            }
        }
        assert mock_ili.mock_calls == [call('local/img.png')]
        assert mock_lifd.mock_calls == [call('local/img.png')]
        assert self.mockapi.mock_calls == [
            call.upload_image(b'imgdata', 'img.png', 'image/png')
        ]

    def test_local_existing_img(self):
        mock_html = E.HTML(
            E.HEAD(E.TITLE('Some Title')),
            E.BODY(
                E.P('Hello\nGoodbye'),
                E.IMG(src='local/img.png')
            )
        )
        root = mock_html.getroottree()
        self.mockapi.upload_image.return_value = (None, None)
        with patch('%s._is_local_image' % pb) as mock_ili:
            with patch('%s._load_image_from_disk' % pb) as mock_lifd:
                mock_ili.return_value = True
                mock_lifd.return_value = (
                    'image/png', b'imgdata', sha256str
                )
                newroot, res = self.cls._upload_images(
                    root,
                    images={
                        sha256str: {
                            'location': 'http://jive.example.com/existing',
                            'jive_object': {
                                'id': '123456',
                                'foo': 'bar'
                            },
                            'local_path': 'my/image/path.png'
                        }
                    }
                )
        imgs = newroot.xpath('//img')
        assert len(imgs) == 1
        assert imgs[0].get('src') == 'http://jive.example.com/existing'
        assert res == {
            sha256str: {
                'location': 'http://jive.example.com/existing',
                'jive_object': {
                    'id': '123456',
                    'foo': 'bar'
                },
                'local_path': 'my/image/path.png'
            }
        }
        assert mock_ili.mock_calls == [call('local/img.png')]
        assert mock_lifd.mock_calls == [call('local/img.png')]
        assert self.mockapi.mock_calls == []
