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
import re
from requests import Response
from requests.utils import guess_json_utf
from requests.compat import json as complexjson

logger = logging.getLogger(__name__)

JIVE_SECURITY_RE = re.compile(r'^throw.*;\s*')


def requests_hook(response, **_):
    """
    :py:class:`requests.Session` ``response`` hook to return
    :py:class:`~.JiveResponse` objects instead of plain
    :py:class:`requests.Response` objects.

    Add this to a :py:class:`requests.Session` like
    ``session.hooks['response'].append(requests_hook)``
    """
    res = JiveResponse()
    res.__dict__.update(response.__dict__)
    return res


class JiveResponse(Response):
    """
    Subclass of :py:class:`requests.Response` to handle automatically
    trimming the `JSON Security String
    <https://developers.jivesoftware.com/api/v3/cloud/rest/index.html
    #security>`_ from the beginning of Jive API responses.
    """

    def json(self, **kwargs):
        """
        Returns the json-encoded content of a response, if any, with the
        leading JSON Security String stripped off.

        :param kwargs: Optional arguments that ``json.loads`` takes.
        :raises ValueError: If the response body does not contain valid json.
        """
        content = self.text
        if not self.encoding and self.content and len(self.content) > 3:
            # No encoding set. JSON RFC 4627 section 3 states we should expect
            # UTF-8, -16 or -32. Detect which one to use; If the detection or
            # decoding fails, fall back to `self.text` (using chardet to make
            # a best guess).
            encoding = guess_json_utf(self.content)
            if encoding is not None:  # nocoverage
                try:
                    content = self.content.decode(encoding)
                except UnicodeDecodeError:
                    # Wrong UTF codec detected; usually because it's not UTF-8
                    # but some other 8-bit codec.  This is an RFC violation,
                    # and the server didn't bother to tell us what codec *was*
                    # used.
                    pass
        content = JIVE_SECURITY_RE.sub('', content)
        return complexjson.loads(content, **kwargs)

    def __repr__(self):
        return '<JiveResponse [%s]>' % self.status_code
