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

import pytest
from datetime import datetime
from requests import Session
from collections import namedtuple

from jiveapi.exceptions import ContentConflictException, RequestFailedException
from jiveapi.api import JiveApi
from jiveapi.jiveresponse import requests_hook
from jiveapi.tests.test_helpers import MockResponse, FixedOffset

from unittest.mock import patch, MagicMock, call

# TEST CONSTANTS - These are specific to the user running the tests when
# new data is recorded

#: The Jive person/user ID of our test user
AUTHOR_ID = '8627'
# END TEST CONSTANTS

pb = 'jiveapi.api.JiveApi'


class TestInit(object):

    def test_default_path(self):
        mock_sess = MagicMock()
        type(mock_sess).hooks = {'response': []}
        with patch('jiveapi.api.requests') as mock_req:
            mock_req.Session.return_value = mock_sess
            cls = JiveApi('http://jive.example.com/', 'uname', 'passwd')
        assert cls._base_url == 'http://jive.example.com/'
        assert cls._username == 'uname'
        assert cls._password == 'passwd'
        assert cls._requests == mock_sess
        assert mock_sess.hooks['response'] == [requests_hook]

    def test_no_trailing_slash(self):
        mock_sess = MagicMock()
        type(mock_sess).hooks = {'response': []}
        with patch('jiveapi.api.requests') as mock_req:
            mock_req.Session.return_value = mock_sess
            cls = JiveApi('http://jive.example.com', 'uname', 'passwd')
        assert cls._base_url == 'http://jive.example.com/'
        assert cls._username == 'uname'
        assert cls._password == 'passwd'
        assert cls._requests == mock_sess
        assert mock_sess.hooks['response'] == [requests_hook]


class TestAbsUrl(object):

    def test_abs_url(self):
        api = JiveApi('http://jive.example.com/api/', 'jiveuser', 'jivepass')
        assert api.abs_url('foo/bar') == 'http://jive.example.com/api/foo/bar'


class TestUser(object):

    def test_user_self_svc_acct(self, api):
        """Recorded API transaction using betamax"""
        res = api.user()
        assert res['jive']['federated'] is True
        assert res['jive']['status'] == 'registered'
        assert res['displayName'] == 'Jason Antman'
        assert res['id'] == '8627'
        assert res['type'] == 'person'
        assert res['name']['givenName'] == 'Jason'


class TestVersion(object):

    def test_version(self, api, jive_host, jive_scheme):
        """Recorded API transaction using betamax"""
        res = api.api_version()
        assert res == {
            'instanceURL': '%s://%s' % (jive_scheme, jive_host),
            'jiveCoreVersions': [
                {
                    'documentation': 'https://developers.jivesoftware.com/'
                                     'api/v2/rest',
                    'revision': 3,
                    'uri': '/api/core/v2',
                    'version': 2
                },
                {
                    'documentation': 'https://developers.jivesoftware.com/'
                                     'api/v3/rest',
                    'revision': 15,
                    'uri': '/api/core/v3',
                    'version': 3
                }
            ],
            'jiveEdition': {
                'product': 'cloud',
                'tier': 999
            },
            'jiveVersion': '2016.3.8.1'
        }


class TestRequestMethods(object):

    def setup(self):
        self.api = JiveApi('http://jive.example.com/', 'jiveuser', 'jivepass')
        self.mock_sess = MagicMock(spec_set=Session)
        self.api._requests = self.mock_sess

    def test_get_http_url(self):
        self.mock_sess.get.side_effect = [
            MockResponse(200, 'OK', _json={
                'links': {
                    'next': 'http://jive.example.com/bar'
                },
                'list': [
                    'one',
                    'two'
                ]
            }),
            MockResponse(200, 'OK', _json={
                'list': [
                    'three'
                ]
            })
        ]
        res = self.api._get('http://jive.example.com/foo', autopaginate=True)
        assert res == ['one', 'two', 'three']
        assert self.mock_sess.mock_calls == [
            call.get('http://jive.example.com/foo'),
            call.get('http://jive.example.com/bar')
        ]

    def test_post_json(self):
        self.mock_sess.post.side_effect = [
            MockResponse(201, 'Created', _json={
                'list': [
                    'three'
                ]
            })
        ]
        res = self.api._post_json(
            'http://jive.example.com/foo', {'foo': 'bar'}
        )
        assert res == {
            'list': [
                'three'
            ]
        }
        assert self.mock_sess.mock_calls == [
            call.post('http://jive.example.com/foo', json={'foo': 'bar'})
        ]

    def test_put_json(self):
        self.mock_sess.put.side_effect = [
            MockResponse(201, 'Created', _json={
                'list': [
                    'three'
                ]
            })
        ]
        res = self.api._put_json(
            'http://jive.example.com/foo', {'foo': 'bar'}
        )
        assert res == {
            'list': [
                'three'
            ]
        }
        assert self.mock_sess.mock_calls == [
            call.put('http://jive.example.com/foo', json={'foo': 'bar'})
        ]


class TestCreateContent(object):

    def test_create_content_exception(self, api):
        """
        Recorded API transaction using betamax. Depends on Jive state.
        """
        content = {
            'type': 'document',
            'subject': 'Test Html Simple',
            'content': {
                'type': 'text/html',
                'text': '<body><p>TestCreateContents.test_html_simple()'
                        '</p></body>'
            }
        }
        with pytest.raises(ContentConflictException) as excinfo:
            api.create_content(content)
        assert excinfo.value.response.url == 'https://sandbox.jiveon.com/' \
                                             'api/core/v3/contents'
        assert excinfo.value.response.status_code == 409
        assert excinfo.value.response.reason == 'Conflict'
        msg = 'A document with the same title already exists in this place'
        assert excinfo.value.error_message == msg

    def test_create_content(self, api):
        """Recorded API transaction using betamax."""
        content = {
            'type': 'document',
            'subject': 'Yet Another HTML Test',
            'content': {
                'type': 'text/html',
                'text': '<body><p>TestCreateContents.test_create_contents()'
                        '</p></body>'
            }
        }
        res = api.create_content(content)
        assert isinstance(res, type({}))
        assert res['entityType'] == 'document'
        assert res['author']['id'] == AUTHOR_ID
        assert res['content']['editable'] is False
        assert res['content']['type'] == 'text/html'
        assert res['content']['text'].startswith('<body>')
        assert '<p>TestCreateContents.test_create_contents()' \
               '</p>' in res['content']['text']
        assert res['content']['text'].endswith('</body>')
        assert res['contentID'] == '1660405'
        assert res['status'] == 'published'
        assert res['subject'] == 'Yet Another HTML Test'
        assert res['authors'][0]['id'] == AUTHOR_ID
        assert res['visibility'] == 'all'
        assert res['authorship'] == 'author'
        assert res['categories'] == []
        assert res['parentVisible'] is True
        assert res['parentContentVisible'] is True
        assert res['restrictComments'] is False
        assert res['editDisabled'] is False
        assert res['version'] == 1
        assert res['attachments'] == []
        assert res['type'] == 'document'

    def test_publish_date(self):
        api = JiveApi('http://jive.example.com/', 'jiveuser', 'jivepass')
        tz = FixedOffset(-60, 'foo')
        with patch('%s._post_json' % pb, autospec=True) as mock_post:
            mock_post.return_value = {'return': 'value'}
            res = api.create_content(
                {'foo': 'bar'},
                publish_date=datetime(2018, 2, 13, 11, 23, 52, tzinfo=tz)
            )
        assert res == {'return': 'value'}
        assert mock_post.mock_calls == [
            call(
                api,
                'core/v3/contents?published=2018-02-13T11%3A23%3A52.000-0100&'
                'updated=2018-02-13T11%3A23%3A52.000-0100',
                {'foo': 'bar'}
            )
        ]

    def test_content_conflict(self):
        api = JiveApi('http://jive.example.com/', 'jiveuser', 'jivepass')
        req_t = namedtuple('MockRequest', ['method', 'url'])
        req = req_t(method='POST', url='http://jive.example.com/')
        with patch('%s._post_json' % pb) as mock_post:
            mock_post.side_effect = RequestFailedException(
                MockResponse(409, 'Conflict', request=req)
            )
            with pytest.raises(ContentConflictException):
                api.create_content({'foo': 'bar'})

    def test_500(self):
        api = JiveApi('http://jive.example.com/', 'jiveuser', 'jivepass')
        req_t = namedtuple('MockRequest', ['method', 'url'])
        req = req_t(method='POST', url='http://jive.example.com/')
        with patch('%s._post_json' % pb) as mock_post:
            mock_post.side_effect = RequestFailedException(
                MockResponse(500, 'Conflict', request=req)
            )
            with pytest.raises(RequestFailedException):
                api.create_content({'foo': 'bar'})


class TestGetContent(object):

    def test_get_content(self, api):
        """Recorded API transaction using betamax. Depends on Jive state"""
        res = api.get_content('1660403')
        assert res['entityType'] == 'document'
        assert res['author']['id'] == AUTHOR_ID
        assert res['tags'] == ['document', 'example']
        assert res['content']['editable'] is False
        assert res['content']['type'] == 'text/html'
        assert res['content']['text'].startswith('<body>')
        assert 'his is the body of some <strong>document</strong>' \
               ' that I created via the web UI. It is public to the entire ' \
               'instance.</p>' in res['content']['text']
        assert res['content']['text'].endswith('</body>')
        assert res['status'] == 'published'
        assert res['subject'] == 'Some Public Document'
        assert res['authors'][0]['id'] == AUTHOR_ID
        assert res['visibility'] == 'all'
        assert res['authorship'] == 'author'
        assert res['categories'] == []
        assert res['parentVisible'] is True
        assert res['parentContentVisible'] is True
        assert res['restrictComments'] is False
        assert res['editDisabled'] is False
        assert res['version'] == 1
        assert res['attachments'] == []
        assert res['type'] == 'document'

    def test_get_content_404(self, api):
        """Recorded API transaction using betamax. Depends on Jive state"""
        with pytest.raises(RequestFailedException) as excinfo:
            api.get_content('99999999')
        assert excinfo.value.response.url == 'https://sandbox.jiveon.com/' \
                                             'api/core/v3/contents/99999999?' \
                                             'directive=silent'
        assert excinfo.value.response.status_code == 404
        assert excinfo.value.response.reason == 'Not Found'
        assert excinfo.value.error_message == 'Missing content ID 99999999'


class TestUpdateContent(object):

    def test_update_content(self, api):
        """Recorded API transaction using betamax. Depends on Jive state"""
        content = {
            'type': 'document',
            'subject': 'Some Public Document Edited',
            'content': {
                'type': 'text/html',
                'text': '<body><p>This is my now-edited body.</p></body>'
            },
            'tags': ['document']
        }
        res = api.update_content('1660403', content)
        assert res['entityType'] == 'document'
        assert res['author']['id'] == AUTHOR_ID
        assert res['tags'] == ['document']
        assert res['content']['editable'] is False
        assert res['content']['type'] == 'text/html'
        assert res['content']['text'].startswith('<body>')
        assert '<p>This is my now-edited body.</p>' in res['content']['text']
        assert res['content']['text'].endswith('</body>')
        assert res['status'] == 'published'
        assert res['subject'] == 'Some Public Document Edited'
        assert res['authors'][0]['id'] == AUTHOR_ID
        assert res['visibility'] == 'all'
        assert res['authorship'] == 'author'
        assert res['categories'] == []
        assert res['parentVisible'] is True
        assert res['parentContentVisible'] is True
        assert res['restrictComments'] is False
        assert res['editDisabled'] is False
        assert res['version'] == 2
        assert res['attachments'] == []
        assert res['type'] == 'document'

    def test_update_content_404(self, api):
        """Recorded API transaction using betamax. Depends on Jive state"""
        content = {
            'type': 'document',
            'subject': 'Some Public Document Edited',
            'content': {
                'type': 'text/html',
                'text': '<body><p>This is my now-edited body.</p></body>'
            },
            'tags': ['document']
        }
        with pytest.raises(RequestFailedException) as excinfo:
            api.update_content('99999999', content)
        assert excinfo.value.response.url == 'https://sandbox.jiveon.com/' \
                                             'api/core/v3/contents/99999999'
        assert excinfo.value.response.status_code == 404
        assert excinfo.value.response.reason == 'Not Found'
        assert excinfo.value.error_message == 'Missing content ID 99999999'

    def test_update_date(self):
        api = JiveApi('http://jive.example.com/', 'jiveuser', 'jivepass')
        tz = FixedOffset(-60, 'foo')
        with patch('%s._put_json' % pb, autospec=True) as mock_put:
            mock_put.return_value = {'return': 'value'}
            res = api.update_content(
                'cid',
                {'foo': 'bar'},
                update_date=datetime(2018, 2, 13, 11, 23, 52, tzinfo=tz)
            )
        assert res == {'return': 'value'}
        assert mock_put.mock_calls == [
            call(
                api,
                'core/v3/contents/cid'
                '?updated=2018-02-13T11%3A23%3A52.000-0100',
                {'foo': 'bar'}
            )
        ]

    def test_content_conflict(self):
        api = JiveApi('http://jive.example.com/', 'jiveuser', 'jivepass')
        req_t = namedtuple('MockRequest', ['method', 'url'])
        req = req_t(method='PUT', url='http://jive.example.com/')
        with patch('%s._put_json' % pb) as mock_put:
            mock_put.side_effect = RequestFailedException(
                MockResponse(409, 'Conflict', request=req)
            )
            with pytest.raises(ContentConflictException):
                api.update_content('cid', {'foo': 'bar'})

    def test_500(self):
        api = JiveApi('http://jive.example.com/', 'jiveuser', 'jivepass')
        req_t = namedtuple('MockRequest', ['method', 'url'])
        req = req_t(method='PUT', url='http://jive.example.com/')
        with patch('%s._put_json' % pb) as mock_put:
            mock_put.side_effect = RequestFailedException(
                MockResponse(500, 'Conflict', request=req)
            )
            with pytest.raises(RequestFailedException):
                api.update_content('cid', {'foo': 'bar'})


class TestGetImage(object):

    def test_success(self):
        api = JiveApi('http://jive.example.com/', 'jiveuser', 'jivepass')
        mock_sess = MagicMock(spec_set=Session)
        api._requests = mock_sess
        mock_sess.get.return_value = MockResponse(200, 'OK', content=b'1234')
        res = api.get_image('imgid')
        assert res == b'1234'
        assert mock_sess.mock_calls == [
            call.get('http://jive.example.com/core/v3/images/imgid')
        ]

    def test_error(self):
        api = JiveApi('http://jive.example.com/', 'jiveuser', 'jivepass')
        mock_sess = MagicMock(spec_set=Session)
        api._requests = mock_sess
        req_t = namedtuple('MockRequest', ['method', 'url'])
        req = req_t(
            method='GET', url='http://jive.example.com/core/v3/images/imgid'
        )
        mock_sess.get.return_value = MockResponse(
            404, 'Not Found', content=b'1234', request=req
        )
        with pytest.raises(RequestFailedException):
            api.get_image('imgid')
        assert mock_sess.mock_calls == [
            call.get('http://jive.example.com/core/v3/images/imgid')
        ]


class TestUploadImage(object):

    def test_success(self):
        api = JiveApi('http://jive.example.com/', 'jiveuser', 'jivepass')
        mock_sess = MagicMock(spec_set=Session)
        api._requests = mock_sess
        mock_sess.post.return_value = MockResponse(
            201, 'Created', _json={'foo': 'bar'},
            headers={'Location': 'http://some.location/'}
        )
        res = api.upload_image(b'1234', 'img.jpg', 'image/jpeg')
        assert res == (
            'http://some.location/', {'foo': 'bar'}
        )
        assert mock_sess.mock_calls == [
            call.post(
                'http://jive.example.com/core/v3/images',
                files={
                    'file': ('img.jpg', b'1234', 'image/jpeg')
                },
                allow_redirects=False
            )
        ]

    def test_error(self):
        api = JiveApi('http://jive.example.com/', 'jiveuser', 'jivepass')
        mock_sess = MagicMock(spec_set=Session)
        api._requests = mock_sess
        req_t = namedtuple('MockRequest', ['method', 'url'])
        req = req_t(
            method='POST', url='http://jive.example.com/core/v3/images'
        )
        mock_sess.post.return_value = MockResponse(
            400, 'Image is too large.', _json={'foo': 'bar'},
            headers={'Location': 'http://some.location/'}, request=req
        )
        with pytest.raises(RequestFailedException):
            api.upload_image(b'1234', 'img.jpg', 'image/jpeg')
        assert mock_sess.mock_calls == [
            call.post(
                'http://jive.example.com/core/v3/images',
                files={
                    'file': ('img.jpg', b'1234', 'image/jpeg')
                },
                allow_redirects=False
            )
        ]


class TestGetContentInPlace(object):

    def test_get_content_in_place(self, api):
        """Recorded API transaction using betamax. Depends on Jive state"""
        res = api.get_content_in_place('94583')
        items = [
            {
                'type': x['type'],
                'subject': x['subject'],
                'contentID': x['contentID']
            }
            for x in res
        ]
        assert items == [
            {'type': 'document', 'subject': 'Test234', 'contentID': '1428798'},
            {
                'type': 'video',
                'subject': 'Lumia 930 camera',
                'contentID': '1378083'
            },
            {
                'type': 'video',
                'subject': 'Cool Engineering',
                'contentID': '1378071'
            },
            {'type': 'idea', 'subject': 'raz Idea', 'contentID': '315384'},
            {'type': 'document', 'subject': 'test', 'contentID': '236115'},
            {'type': 'discussion', 'subject': 'Hallo', 'contentID': '236081'},
            {'type': 'document', 'subject': 'tyest', 'contentID': '129727'},
            {'type': 'discussion', 'subject': 'test', 'contentID': '107175'}
        ]

    def test_get_content_in_place_blog(self, api):
        """Recorded API transaction using betamax. Depends on Jive state"""
        res = api.get_content_in_place('94584')
        items = [
            {
                'type': x['type'],
                'subject': x['subject'],
                'contentID': x['contentID']
            }
            for x in res
        ]
        assert items == [
            {'type': 'post', 'subject': 'example', 'contentID': '129269'}
        ]

    def test_get_content_404(self, api):
        """Recorded API transaction using betamax. Depends on Jive state"""
        with pytest.raises(RequestFailedException) as excinfo:
            api.get_content_in_place('99999999899')
        assert excinfo.value.response.url == 'https://sandbox.jiveon.com/' \
                                             'api/core/v3/places/99999999899/' \
                                             'contents'
        assert excinfo.value.response.status_code == 404
        assert excinfo.value.response.reason == 'Not Found'
        assert excinfo.value.error_message == 'Invalid place URI https://' \
                                              'sandbox.jiveon.com/api/core/' \
                                              'v3/places/99999999899/contents'
