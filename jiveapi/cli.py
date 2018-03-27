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
import argparse
import logging

from jiveapi.api import JiveApi
from jiveapi.utils import set_log_debug, set_log_info, prettyjson
from jiveapi.version import PROJECT_URL, VERSION

logger = logging.getLogger(__name__)

for lname in ['requests', 'urllib', 'urllib3']:
    l = logging.getLogger(lname)
    l.setLevel(logging.WARNING)
    l.propagate = True


class JiveApiCli(object):

    def __init__(self, base_url, username, password):
        self._api = JiveApi(base_url, username, password)

    def show_user_info(self):
        user = self._api.user()
        username = user.get('jive', {}).get('username', '')
        print(
            'Authenticated to Jive as "%s" (id %s) %s' % (
                user['displayName'], user['id'], username
            )
        )
        print('\tUser type %s (%s)' % (user['typeCode'], user['type']))
        print('\tEmails: %s' % ', '.join([
            e['value'] for e in sorted(
                user['emails'], key=lambda x: x.get('jive_displayOrder', 0)
            )
        ]))
        print(
            '\tThumbnail %s: %s' % (user['thumbnailId'], user['thumbnailUrl'])
        )
        print('\tInitial Login: %s - Updated %s' % (
            user['initialLogin'], user['updated']
        ))
        if 'jive' in user:
            j = user['jive']
            jive_items = [
                'enabled', 'external', 'externalContributor', 'federated',
                'lastAuthenticated', 'lastProfileUpdate', 'status', 'visible'
            ]
            print(
                '\t%s' % ' '.join([
                    '%s=%s' % (i, j[i]) for i in j.keys() if i in jive_items
                ])
            )

    def show_version(self):
        print(prettyjson(self._api.api_version()))


def parse_args():
    """
    Parse command-line arguments.
    """
    p = argparse.ArgumentParser(
        prog='jiveapi', description='Jive API command line client (AGPLv3)'
    )
    p.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                   help='verbose output. specify twice for debug-level output.')
    p.add_argument('-V', '--version', action='version',
                   version='%(prog)s ' + '%s <%s>' % (VERSION, PROJECT_URL))
    p.add_argument('-U', '--url', dest='baseurl', action='store', type=str,
                   default=None,
                   help='Jive API base URL (https://example.com/api/); if not '
                        'specified will be taken from JIVE_URL env var')
    p.add_argument('-u', '--user', dest='username', action='store', type=str,
                   default=None,
                   help='Jive API Username (HTTP Basic Auth); if not '
                        'specified will be taken from JIVE_USER env var')
    p.add_argument('-p', '--pass', dest='password', action='store', type=str,
                   default=None,
                   help='Jive API Password (HTTP Basic Auth); if not '
                        'specified will be taken from JIVE_PASS env var')
    subp = p.add_subparsers(title='subcommands')

    # Current User Info
    user = subp.add_parser(
        'userinfo', help='Return information about the current user'
    )
    user.set_defaults(action='userinfo')

    # API Version Info
    ver = subp.add_parser(
        'version', help='Return the Jive API\'s full version JSON response'
    )
    ver.set_defaults(action='version')

    args = p.parse_args()
    if args.baseurl is None:
        args.baseurl = os.environ.get('JIVE_URL', None)
    if args.username is None:
        args.username = os.environ.get('JIVE_USER', None)
    if args.password is None:
        args.password = os.environ.get('JIVE_PASS', None)
    return args


def main():
    """
    Main entry point - instantiate and run :py:class:`~.OfxBackfiller`.
    """
    global logger
    format = "[%(asctime)s %(levelname)s] %(message)s"
    logging.basicConfig(level=logging.WARNING, format=format)
    logger = logging.getLogger()

    args = parse_args()

    # set logging level
    if args.verbose > 1:
        set_log_debug(logger)
    elif args.verbose == 1:
        set_log_info(logger)

    cli = JiveApiCli(args.baseurl, args.username, args.password)
    if args.action == 'userinfo':
        cli.show_user_info()
    elif args.action == 'version':
        cli.show_version()
    else:
        logger.error('ERROR: Unknown or unspecified action.')
        raise SystemExit(1)


if __name__ == "__main__":
    main()
