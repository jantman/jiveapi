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

from collections import namedtuple

from jiveapi.tests.test_helpers import MockResponse
from jiveapi.exceptions import RequestFailedException, ContentConflictException


req_t = namedtuple('MockRequest', ['method', 'url'])


class TestRequestFailedException(object):

    def test_simple(self):
        req = req_t('GET', 'http://www.example.com')
        resp = MockResponse(
            404, 'Not Found', request=req, no_text=True
        )
        exc = RequestFailedException(resp)
        assert exc.response == resp
        assert exc.status_code == 404
        assert exc.reason == 'Not Found'
        assert str(
            exc
        ) == 'GET http://www.example.com returned HTTP 404 Not Found'

    def test_simple_error_json(self):
        req = req_t('GET', 'http://www.example.com')
        resp = MockResponse(
            404, 'Not Found', request=req,
            _json={'error': {'message': 'errMsg'}}
        )
        exc = RequestFailedException(resp)
        assert exc.response == resp
        assert exc.status_code == 404
        assert exc.reason == 'Not Found'
        assert str(
            exc
        ) == 'GET http://www.example.com returned HTTP 404 Not Found: errMsg'

    def test_simple_text(self):
        req = req_t('GET', 'http://www.example.com')
        resp = MockResponse(
            404, 'Not Found', request=req,
            text='errText'
        )
        exc = RequestFailedException(resp)
        assert exc.response == resp
        assert exc.status_code == 404
        assert exc.reason == 'Not Found'
        assert str(
            exc
        ) == 'GET http://www.example.com returned HTTP 404 Not Found: errText'


class TestContentConflictException(object):

    def test_simple(self):
        req = req_t('GET', 'http://www.example.com')
        resp = MockResponse(
            409, 'Conflict', request=req
        )
        exc = ContentConflictException(resp)
        assert exc.response == resp
        assert exc.status_code == 409
        assert exc.reason == 'Conflict'
        assert str(
            exc
        ) == 'GET http://www.example.com returned HTTP 409 Conflict: ' \
             'The new entity would conflict with system restrictions ' \
             '(such as two contents of the same type with the same name)'

    def test_simple_error_json(self):
        req = req_t('GET', 'http://www.example.com')
        resp = MockResponse(
            409, 'Conflict', request=req, _json={'error': {'message': 'eMsg'}}
        )
        exc = ContentConflictException(resp)
        assert exc.response == resp
        assert exc.status_code == 409
        assert exc.reason == 'Conflict'
        assert str(
            exc
        ) == 'GET http://www.example.com returned HTTP 409 Conflict: eMsg'

    def test_simple_no_json(self):
        req = req_t('GET', 'http://www.example.com')
        resp = MockResponse(
            409, 'Conflict', request=req, _json={'foo': 'bar'}
        )
        exc = ContentConflictException(resp)
        assert exc.response == resp
        assert exc.status_code == 409
        assert exc.reason == 'Conflict'
        assert str(
            exc
        ) == 'GET http://www.example.com returned HTTP 409 Conflict: ' \
             'The new entity would conflict with system restrictions ' \
             '(such as two contents of the same type with the same name)'
