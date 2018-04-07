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

from docutils import nodes
from docutils.writers.html4css1 import HTMLTranslator as BaseTranslator

from sphinx.locale import __
from sphinx.builders.html import SingleFileHTMLBuilder
from sphinx.writers.html import HTMLTranslator


class JiveHtmlTranslator(HTMLTranslator):
    """
    Subclass of sphinx's built-in ``HTMLTranslator`` to fix some output nuances.
    Mainly, Jive overwrites "id" elements on everything, so named anchors need
    to use the deprecated ``name`` attribute. We also need to identify internal
    hrefs that link to ``index.html#something`` and strip the leading filename.
    """

    def add_permalink_ref(self, node, title):
        # type: (nodes.Node, unicode) -> None
        if node['ids'] and self.permalink_text and self.builder.add_permalinks:
            fmt = u'<a name="%s"></a>'
            self.body.append(
                fmt % node['ids'][0]
            )

    def depart_title(self, node):
        # type: (nodes.Node) -> None
        close_tag = self.context[-1]
        if (self.permalink_text and self.builder.add_permalinks and
           node.parent.hasattr('ids') and node.parent['ids']):
            # add permalink anchor
            if close_tag.startswith('</h'):
                self.add_permalink_ref(
                    node.parent, None
                )
            elif close_tag.startswith('</a></h'):
                self.body.append(u'</a><a name="%s" >' % node.parent['ids'][0])
            elif isinstance(node.parent, nodes.table):
                self.body.append('</span>')
                self.add_permalink_ref(
                    node.parent, None
                )
        elif isinstance(node.parent, nodes.table):
            self.body.append('</span>')
        BaseTranslator.depart_title(self, node)

    def visit_reference(self, node):
        # type: (nodes.Node) -> None
        atts = {'class': 'reference'}
        if node.get('internal') or 'refuri' not in node:
            atts['class'] += ' internal'
        else:
            atts['class'] += ' external'
        if 'refuri' in node:
            if node.get('refuri') is None:
                atts['href'] = '#'
            elif node['refuri'][0:11] == 'index.html#':
                # strip leading index.html
                atts['href'] = node['refuri'][10:]
            else:
                atts['href'] = node['refuri']
            if self.settings.cloak_email_addresses and \
               atts['href'].startswith('mailto:'):
                atts['href'] = self.cloak_mailto(atts['href'])
                self.in_mailto = 1
        else:
            assert 'refid' in node, \
                   'References must have "refuri" or "refid" attribute.'
            atts['href'] = '#' + node['refid']
        if not isinstance(node.parent, nodes.TextElement):
            assert len(node) == 1 and isinstance(node[0], nodes.image)
            atts['class'] += ' image-reference'
        if 'reftitle' in node:
            atts['title'] = node['reftitle']
        if 'target' in node:
            atts['target'] = node['target']
        self.body.append(self.starttag(node, 'a', '', **atts))

        if node.get('secnumber'):
            self.body.append(('%s' + self.secnumber_suffix) %
                             '.'.join(map(str, node['secnumber'])))


class JiveapiBuilder(SingleFileHTMLBuilder):
    """
    Subclass of sphinx's built-in ``SingleFileHTMLBuilder`` to use
    ``JiveHtmlTranslator`` in place of sphinx's built-in ``HTMLTranslator``.
    """

    name = 'jiveapi'
    epilog = __('The Jive HTML page is in %(outdir)s.')
    script_files = []

    @property
    def default_translator_class(self):
        # type: () -> nodes.NodeVisitor
        return JiveHtmlTranslator


def setup(app):
    # See http://www.sphinx-doc.org/en/stable/theming.html
    app.add_builder(JiveapiBuilder)
