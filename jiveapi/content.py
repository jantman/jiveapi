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

logger = logging.getLogger(__name__)

#: API url param timestamp format, like '2012-01-31T22:46:12.044+0000'
#: note that sub-second time is ignored and set to zero.
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.000%z'


class JiveContent(object):

    def __init__(self, api):
        """
        Initialize the JiveContent wrapper.

        :param api: authenticated API instance
        :type api: jiveapi.api.JiveApi
        """
        self._api = api

    def create_html_document(self, subject, body):
        """
        Create a HTML Document in Jive. This is a convenience wrapper around
        :py:meth:`~.create_content` to assist with forming the content JSON.

        Note that this cannot be used for Documents with attachments (i.e.
        images); you either need to upload the attachments separately or
        use @TODO.

        :param subject: The subject / title of the Document.
        :type subject: str
        :param body: The HTML body of the Document. See the notes in the jiveapi
          package documentation about HTML handling.
        :type body: str
        :return: representation of the created Document content object
        :rtype: dict
        """
        content = {
            'type': 'document',
            'subject': subject,
            'content': {
                'type': 'text/html',
                'text': body
            }
        }
        return self._api.create_content(content)

    @staticmethod
    def jiveize_html(html):
        raise NotImplementedError()

"""
## Document with embedded images GET example:

  "content" : {
    "text" : "<body><!-- [DocumentBodyStart:1693a4b1-d031-49cf-89f0-c768af9badbd] --><div class=\"jive-rendered-content\"><p>This is one image&#160;<a href=\"https://<JIVE-HOST>/servlet/JiveServlet/showImage/102-181245-3-601173/20x20.png\"><img alt=\"image description 20x20\" class=\"image-2 jive-image j-img-original\" height=\"20\" src=\"https://<JIVE-HOST>/servlet/JiveServlet/downloadImage/102-181245-3-601173/20x20.png\" style=\"height: auto;\" width=\"20\"/></a> and this is another:&#160;<a href=\"https://<JIVE-HOST>/servlet/JiveServlet/showImage/102-181245-3-601172/25x25.png\"><img alt=\"image description 25x25\" class=\"image-1 jive-image j-img-original\" height=\"25\" src=\"https://<JIVE-HOST>/servlet/JiveServlet/downloadImage/102-181245-3-601172/25x25.png\" style=\"height: auto;\" width=\"25\"/></a></p></div><!-- [DocumentBodyEnd:1693a4b1-d031-49cf-89f0-c768af9badbd] --></body>",
    "editable" : false,
    "type" : "text/html"
  },
  "contentImages" : [ {
    "id" : "601172",
    "ref" : "https://<JIVE-HOST>/api/core/v3/images/601172?a=1522455592480",
    "size" : 167,
    "width" : 25,
    "height" : 25,
    "type" : "image",
    "typeCode" : 111
  }, {
    "id" : "601173",
    "ref" : "https://<JIVE-HOST>/api/core/v3/images/601173?a=1522455592433",
    "size" : 165,
    "width" : 20,
    "height" : 20,
    "type" : "image",
    "typeCode" : 111
  } ],
  "attachments" : [ ],

## Adding Embedded Images to Content:
https://community.jivesoftware.com/docs/DOC-233174#jive_content_id_Adding_Embedded_Images_to_a_Piece_of_Content

1. Upload Image (POST multipart/form-data) See: Images Service
2. Read Location HTTP Header for API URI for Image
3. Add HTML Markup in Content Body using the new API URI for the Image, see: Contents Service > Update Content
  * May find value in the Contents Service > Update Editable Content if you want to leverage RTE macros.
    * Note the documentation callout : The input JSON must include a true value in content.editable if the content body is using RTE macros.

## Stuff about Editable Content and RTE Macros
https://developers.jivesoftware.com/api/v3/cloud/rest/ContentService.html#updateEditableContent(String, String, boolean, boolean, String)

## Performance Note:
see https://community.jivesoftware.com/docs/DOC-233174#jive_content_id_Suppressing_Fields_from_API_Responses

"""
