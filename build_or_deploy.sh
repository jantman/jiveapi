#!/bin/bash -x
# jiveapi Docker build and push script
################################################################################
# The latest version of this package is available at:
#<http://github.com/jantman/jiveapi>
#
################################################################################
#Copyright 2017 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
#
#    This file is part of jiveapi, also known as jiveapi.
#
#    jiveapi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    jiveapi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with jiveapi.  If not, see <http://www.gnu.org/licenses/>.
#
#The Copyright and Authors attributions contained herein may not be removed or
#otherwise altered, except to add the Author attribution of a contributor to
#this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
#While not legally required, I sincerely request that anyone who finds
#bugs please submit them at <https://github.com/jantman/jiveapi> or
#to me via email, and that you send any contributions or improvements
#either as a pull request on GitHub, or to me via email.
################################################################################
#
#AUTHORS:
#Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################

set -x

if [ -z "$1" ]; then
    >&2 echo "USAGE: do_docker.sh [build|dockerbuild|push]"
    exit 1
fi

function gettag {
    # if it's a build of a tag, return that right away
    [ ! -z "$TRAVIS_TAG" ] && { echo $TRAVIS_TAG; return 0; }
    # otherwise, prefix with PR number if available
    prefix=''
    [ ! -z "$TRAVIS_PULL_REQUEST" ] && [[ "$TRAVIS_PULL_REQUEST" != "false" ]] && prefix="PR${TRAVIS_PULL_REQUEST}_"
    ref="test_${prefix}$(git rev-parse --short HEAD)_$(date +%s)"
    echo "${ref}"
}

function getversion {
    python -c 'from jiveapi.version import VERSION; print(VERSION)'
}

function dockerbuild {
    tag=$(gettag)
    version=$(getversion)
    echo "Building Docker image..."
    cp "${TOXDISTDIR}/jiveapi-${version}.zip" jiveapi.zip
    docker build --build-arg version="$tag" --build-arg jiveapi_version="$version" --no-cache -t "jantman/jiveapi:${tag}" .
    echo "Built image and tagged as: jantman/jiveapi:${tag}"
}

function pythonbuild {
    rm -Rf dist
    python setup.py sdist bdist_wheel
    ls -l dist
}

function dockerpush {
    tag=$(gettag)
    if [[ "$TRAVIS" == "true" ]]; then
        echo "$DOCKER_HUB_PASS" | docker login -u "$DOCKER_HUB_USER" --password-stdin
    fi
    docker images
    echo "Pushing Docker image: jantman/jiveapi:${tag}"
    docker push "jantman/jiveapi:${tag}"
}

function pythonpush {
    pip install twine
    twine upload dist/*
}

if [[ "$1" == "build" ]]; then
    dockerbuild
    pythonbuild
if [[ "$1" == "dockerbuild" ]]; then
    dockerbuild
elif [[ "$1" == "push" ]]; then
    dockerpush
    pythonpush
else
    >&2 echo "USAGE: do_docker.sh [build|dockerbuild|push]"
    exit 1
fi
