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
import sys

japi_ver = sys.argv[1]
print('Expected jiveapi VERSION: %s' % japi_ver)

from jiveapi.version import VERSION
print('jiveapi version: %s' % VERSION)

if japi_ver != VERSION:
    raise SystemExit('ERROR: wrong jiveapi VERSION')

from jiveapi.api import JiveApi
from jiveapi.content import JiveContent

JiveContent.jiveize_html('<p>foo</p>')

import sphinx
print('Sphinx version: %s' % sphinx.__version__)

import boto3
print('boto3 version: %s' % boto3.__version__)

import sphinx_rtd_theme
print('sphinx_rtd_theme version: %s' % sphinx_rtd_theme.__version__)

import rinoh.version
print('rinohtype version: %s' % rinoh.version.__version__)
