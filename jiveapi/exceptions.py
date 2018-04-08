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


class RequestFailedException(RuntimeError):
    """
    Exception raised when a Jive server response contains a HTTP status code
    that indicates an error, or is not the expected status code for the
    request.
    """

    def __init__(self, response):
        """
        :param response: the response that generated this exception
        :type response: :py:class:`requests.Response`
        """
        self.error_message = None
        message = self._message_for_response(response)
        super(RequestFailedException, self).__init__(message)
        self.response = response
        self.status_code = response.status_code
        self.reason = response.reason

    def _message_for_response(self, resp):
        m = '%s %s returned HTTP %s %s' % (
            resp.request.method, resp.request.url, resp.status_code,
            resp.reason
        )
        try:
            j = resp.json()
            if 'error' in j and 'message' in j['error']:
                self.error_message = j['error']['message']
        except Exception:
            try:
                self.error_message = resp.text
            except Exception:
                pass
        if self.error_message is not None:
            m += ': %s' % self.error_message
        return m


class ContentConflictException(RequestFailedException):
    """
    Exception raised when the Jive server response indicates that there is
    a conflict between the submitted content and content already in the system,
    such as two content objects of the same type with the same name.
    """

    def _message_for_response(self, resp):
        desc = 'The new entity would conflict with system restrictions ' \
               '(such as two contents of the same type with the same name)'
        try:
            j = resp.json()
            if 'error' in j and 'message' in j['error']:
                desc = j['error']['message']
        except Exception:
            pass
        self.error_message = desc
        return '%s %s returned HTTP %s %s: %s' % (
            resp.request.method, resp.request.url, resp.status_code,
            resp.reason, desc
        )
