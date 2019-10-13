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

from setuptools import setup, find_packages
from jiveapi.version import VERSION, PROJECT_URL

with open('README.rst') as file:
    long_description = file.read()

requires = [
    'requests < 3.0.0',
    'premailer >=3.0.0, <4.0.0',
    'lxml >=4.0.0, <5.0.0'
]


classifiers = [
    'Development Status :: 7 - Inactive',
    'License :: OSI Approved :: GNU Affero General Public License '
    'v3 or later (AGPLv3+)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Documentation',
    'Topic :: Office/Business'
]

setup(
    name='jiveapi',
    version=VERSION,
    author='Jason Antman',
    author_email='jason@jasonantman.com',
    zip_safe=False,
    packages=find_packages(),
    package_data={
        'jiveapi.sphinx_theme': [
            'theme.conf',
            '*.html'
        ]
    },
    include_package_data=True,
    url=PROJECT_URL,
    description='Simple and limited Python client for Jive collaboration '
                'software ReST API v3.',
    long_description=long_description,
    install_requires=requires,
    keywords="jive collaboration client",
    classifiers=classifiers,
    entry_points={
        'sphinx.html_themes': [
            'jiveapi = jiveapi.sphinx_theme'
        ],
        'sphinx.builders': [
            'jiveapi = jiveapi.sphinx_theme.builder'
        ]
    }
)
