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

import os
import base64
from urllib.parse import urlparse

import pytest
import betamax
from betamax_serializers import pretty_json
from betamax.cassette import cassette

from jiveapi.api import JiveApi


if 'TOXINIDIR' in os.environ:
    fixture_dir = os.path.join(
        os.environ['TOXINIDIR'], 'jiveapi', 'tests', 'fixtures'
    )
    cassette_dir = os.path.join(fixture_dir, 'cassettes')
else:
    fixture_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'fixtures'
    ))
    cassette_dir = os.path.join(fixture_dir, 'cassettes')


if 'JIVE_URL' not in os.environ:
    os.environ['JIVE_URL'] = 'https://sandbox.jiveon.com/api'


def pytest_addoption(parser):
    parser.addoption('--record', action='store_true', default=False,
                     help='allow recording of new betamax cassettes')


def betamax_sanitizer(interaction, current_cassette):
    """betamax data sanitizer for dynamic data"""
    headers = interaction.data['response']['headers']
    for h in headers.get('Set-Cookie', []):
        if 'BIGip' in h:
            current_cassette.placeholders.append(
                cassette.Placeholder(
                    placeholder='<BIG-IP-COOKIE>',
                    replace=h
                )
            )


@pytest.fixture
def fixtures_path():
    return os.path.abspath(fixture_dir)


@pytest.fixture
def jive_domain(jive_host):
    parts = jive_host.split('.')
    return '%s.%s' % (parts[-2], parts[-1])


@pytest.fixture
def jive_host():
    return urlparse(os.environ['JIVE_URL']).hostname


@pytest.fixture
def jive_scheme():
    return urlparse(os.environ['JIVE_URL']).scheme


@pytest.fixture
def api_and_betamax(request, jive_domain, jive_host):
    conf = betamax.Betamax.configure()
    conf.default_cassette_options['serialize_with'] = 'prettyjson'
    conf.cassette_library_dir = cassette_dir
    betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
    # keep creds secret
    conf.define_cassette_placeholder(
        '<JIVE-AUTH>',
        base64.b64encode(
            '{0}:{1}'.format(
                os.environ['JIVE_USER'], os.environ['JIVE_PASS']
            ).encode('utf-8')
        ).decode()
    )
    conf.define_cassette_placeholder('<JIVE-USER>', os.environ['JIVE_USER'])
    conf.define_cassette_placeholder('<JIVE-PASS>', os.environ['JIVE_PASS'])
    conf.define_cassette_placeholder('<JIVE-HOST>', jive_host)
    conf.define_cassette_placeholder('<JIVE-DOMAIN>', jive_domain)
    conf.before_record(callback=betamax_sanitizer)
    if request.config.getoption('--record'):
        conf.default_cassette_options['record_mode'] = 'once'
    else:
        conf.default_cassette_options['record_mode'] = 'none'
    cass_name = betamax.fixtures.pytest._casette_name(
        request, parametrized=True
    )
    api = JiveApi(
        os.environ['JIVE_URL'], os.environ['JIVE_USER'], os.environ['JIVE_PASS']
    )
    # Workaround for https://github.com/betamaxpy/betamax/issues/124
    # where secrets aren't stripped from gzipped responses. Fix is to tell the
    # server that we can't accept gzip.
    api._requests.headers.update({'Accept-Encoding': 'identity'})
    bmax = betamax.Betamax(api._requests)
    bmax.use_cassette(cass_name)
    bmax.start()
    request.addfinalizer(bmax.stop)
    return api, bmax


@pytest.fixture
def api(api_and_betamax):
    return api_and_betamax[0]


@pytest.fixture
def bmax(api_and_betamax):
    return api_and_betamax[1]
