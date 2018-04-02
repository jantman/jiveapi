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

from datetime import datetime
from urllib.parse import urljoin
from unittest.mock import Mock, call, patch

from jiveapi.content import JiveContent
from jiveapi.api import JiveApi
from jiveapi.tests.test_helpers import FixedOffset
from jiveapi.version import VERSION, PROJECT_URL

pbm = 'jiveapi.content'


class TestInit(object):

    def test_init(self):
        m_api = Mock()
        cls = JiveContent(m_api)
        assert cls._api == m_api


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
