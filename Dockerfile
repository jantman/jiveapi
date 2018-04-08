# jiveapi Dockerfile
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
FROM python:3.6.5-alpine3.7

ARG version
ARG jiveapi_version
USER root

COPY jiveapi.zip /tmp/jiveapi.zip
COPY docker_image_test.py /tmp/docker_image_test.py

RUN set -ex \
    && apk add --no-cache \
         libxml2 \
         libxml2-dev \
         libxslt \
         libxslt-dev \
         bash \
    && apk add --no-cache --virtual .build-deps \
         gcc \
         linux-headers \
         musl-dev \
         openssl-dev \
    && pip install /tmp/jiveapi.zip \
    && pip install sphinx rinohtype boto3 sphinx_rtd_theme \
    && apk del .build-deps \
    && rm -f /tmp/jiveapi.zip \
    && python /tmp/docker_image_test.py $jiveapi_version

ENV LANG=en_US.UTF-8

LABEL com.jasonantman.jiveapi.version=$version
LABEL maintainer="jason@jasonantman.com"
LABEL homepage="http://github.com/jantman/jiveapi"
LABEL version=$version

ENTRYPOINT ["/bin/bash"]
