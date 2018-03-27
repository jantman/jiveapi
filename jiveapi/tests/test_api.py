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

pbm = 'jiveapi.utils'


class TestUser(object):

    def test_user_self_svc_acct(self, api):
        res = api.user()
        assert res['jive']['federated'] is True
        assert res['jive']['status'] == 'registered'
        assert res['displayName'] == 'Jason Antman'
        assert res['id'] == '8627'
        assert res['type'] == 'person'
        assert res['name']['givenName'] == 'Jason'


class TestVersion(object):

    def test_version(self, api, jive_host, jive_scheme):
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
