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

from unittest.mock import patch, call

from jiveapi.jiveresponse import JiveResponse

pbm = 'jiveapi.jiveresponse'
pb = '%s.JiveResponse' % pbm


class TestJiveResponse(object):

    def test_with_security_string(self):
        cls = JiveResponse()
        cls.encoding = 'utf-8'
        cls.status_code = 200
        cls._content = 'throw \'allowIllegalResourceCall is false.\';{"foo": ' \
                       '"bar", "baz": "blam"}'.encode('utf-8')
        with patch('%s.complexjson' % pbm) as mock_cj:
            cls.json()
        assert mock_cj.mock_calls == [
            call.loads('{"foo": "bar", "baz": "blam"}')
        ]

    def test_no_security_string(self):
        cls = JiveResponse()
        cls.encoding = 'utf-8'
        cls.status_code = 200
        cls._content = '{"foo": "bar", "baz": "blam"}'.encode('utf-8')
        with patch('%s.complexjson' % pbm) as mock_cj:
            cls.json()
        assert mock_cj.mock_calls == [
            call.loads('{"foo": "bar", "baz": "blam"}')
        ]

    def test_no_encoding_set(self):
        cls = JiveResponse()
        cls.status_code = 200
        cls._content = '{"foo": "bar", "baz": "blam"}'.encode('utf-8')
        with patch('%s.complexjson' % pbm) as mock_cj:
            cls.json()
        assert mock_cj.mock_calls == [
            call.loads('{"foo": "bar", "baz": "blam"}')
        ]

    def test_non_utf_encoding(self):
        cls = JiveResponse()
        cls.status_code = 200
        cls._content = '{"foo": "bar", "baz": "blam"}'.encode('ascii')
        with patch('%s.complexjson' % pbm) as mock_cj:
            cls.json()
        assert mock_cj.mock_calls == [
            call.loads('{"foo": "bar", "baz": "blam"}')
        ]

    def test_kwargs(self):
        cls = JiveResponse()
        cls.status_code = 200
        cls.encoding = 'utf-8'
        cls._content = '{"foo": "bar", "baz": "blam"}'.encode('utf-8')
        with patch('%s.complexjson' % pbm) as mock_cj:
            cls.json(foo='bar')
        assert mock_cj.mock_calls == [
            call.loads('{"foo": "bar", "baz": "blam"}', foo='bar')
        ]

    def test_repr(self):
        cls = JiveResponse()
        cls.status_code = 200
        cls.encoding = 'utf-8'
        cls._content = '{"foo": "bar", "baz": "blam"}'.encode('utf-8')
        assert str(cls) == '<JiveResponse [200]>'
