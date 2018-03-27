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
import requests
from urllib.parse import urljoin

from jiveapi.jiveresponse import requests_hook

logger = logging.getLogger(__name__)


class JiveApi(object):

    def __init__(self, base_url, username, password):
        self._base_url = base_url
        if not self._base_url.endswith('/'):
            self._base_url += '/'
        self._username = username
        self._password = password
        self._requests = requests.Session()
        # add the requests hook to use JiveResponse() class
        self._requests.hooks['response'].append(requests_hook)
        # setup auth
        self._requests.auth = (self._username, self._password)

    def _get(self, path):
        url = urljoin(self._base_url, path)
        logger.debug('GET %s', url)
        res = self._requests.get(url)
        logger.debug('GET %s returned status %d', url, res.status_code)
        res.raise_for_status()
        return res

    def user(self, id_number='@me'):
        return self._get('core/v3/people/%s' % id_number).json()

    def api_version(self):
        return self._get('version').json()
