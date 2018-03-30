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

from jiveapi.exceptions import ContentConflictException, RequestFailedException

# TEST CONSTANTS - These are specific to the user running the tests when
# new data is recorded

#: The Jive person/user ID of our test user
AUTHOR_ID = '8627'

# END TEST CONSTANTS

pbm = 'jiveapi.utils'


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


class TestCreateContents(object):

    def test_create_contents_exception(self, api):
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
            api.create_contents(content)
        assert excinfo.value.response.url == 'https://sandbox.jiveon.com/' \
                                             'api/core/v3/contents'
        assert excinfo.value.response.status_code == 409
        assert excinfo.value.response.reason == 'Conflict'
        msg = 'A document with the same title already exists in this place'
        assert excinfo.value.error_message == msg

    def test_create_contents(self, api):
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
        res = api.create_contents(content)
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


class TestGetContents(object):

    def test_get_contents(self, api):
        """Recorded API transaction using betamax. Depends on Jive state"""
        res = api.get_contents('1660403')
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

    def test_get_contents_404(self, api):
        """Recorded API transaction using betamax. Depends on Jive state"""
        with pytest.raises(RequestFailedException) as excinfo:
            api.get_contents('99999999')
        assert excinfo.value.response.url == 'https://sandbox.jiveon.com/' \
                                             'api/core/v3/contents/99999999'
        assert excinfo.value.response.status_code == 404
        assert excinfo.value.response.reason == 'Not Found'
        assert excinfo.value.error_message == 'Missing content ID 99999999'
