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
import json

from jiveapi.utils import (
    set_log_level_format, set_log_info, set_log_debug, prettyjson
)

from unittest.mock import patch, call, Mock

pbm = 'jiveapi.utils'


class TestUtils(object):

    def test_set_log_info(self):
        mock_log = Mock(spec_set=logging.Logger)
        with patch('%s.set_log_level_format' % pbm) as mock_set:
            set_log_info(mock_log)
        assert mock_set.mock_calls == [
            call(
                mock_log, logging.INFO,
                '%(asctime)s %(levelname)s:%(name)s:%(message)s'
            )
        ]

    def test_set_log_debug(self):
        mock_log = Mock(spec_set=logging.Logger)
        with patch('%s.set_log_level_format' % pbm) as mock_set:
            set_log_debug(mock_log)
        assert mock_set.mock_calls == [
            call(mock_log, logging.DEBUG,
                 "%(asctime)s [%(levelname)s %(filename)s:%(lineno)s - "
                 "%(name)s.%(funcName)s() ] %(message)s")
        ]

    def test_set_log_level_format(self):
        mock_log = Mock(spec_set=logging.Logger)
        mock_handler = Mock(spec_set=logging.Handler)
        type(mock_log).handlers = [mock_handler]
        with patch('%s.logging.Formatter' % pbm) as mock_formatter:
            set_log_level_format(mock_log, 5, 'foo')
        assert mock_formatter.mock_calls == [
            call(fmt='foo')
        ]
        assert mock_handler.mock_calls == [
            call.setFormatter(mock_formatter.return_value)
        ]
        assert mock_log.mock_calls == [
            call.setLevel(5)
        ]

    def test_prettyjson(self):
        d = {'foo': 'bar', 'bar': 'baz'}
        assert json.dumps(
            d, sort_keys=True, indent=4, separators=(',', ': ')
        ) == prettyjson(d)
