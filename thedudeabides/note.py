# -*- coding: utf-8 -*-

from jinja2 import Environment, PackageLoader

from pathlib import Path
from datetime import date
from frontmatter import load, loads, dumps
# from pprint import pprint

import logging
log = logging.getLogger(__name__)


class Note(object):

    """Encapsulate a Markdown file on disk. Note is usually created by
    Zettelkasten. A Note provides common operations for Notes.

    """
    _env = None

    def __init__(self, md, ident, filename=None, contents=None,
                 display_id=True):
        """Constructor.

        :md: Markdown parser instance
        :ident: unique identifier for the Note
        :filename: filename of Note file. Can be relative or absolute
        :contents: contents for Note. If not provided, filename is loaded on
                 first use
        :display_id: True if ID must be output when rendering, False when not

        """
        self.ident = ident
        self.filename = filename
        self.contents = load(filename) if contents is None else loads(contents)
        self.display_id = display_id
        self.front_matter = None
        # Parsed contents
        self.md = md
        self.T = self.md.parse(self.get_body())

    def __eq__(self, other):
        """Compare Note instances by unique identifier.
        """
        return self.ident == other

    def __lt__(self, other):
        """TODO: Docstring for __lt__.
        """
        if isinstance(other, Note):
            other = other.get_id()
        return self.ident < other

    def __repr__(self):
        """Return the Note title if cast to string().

        :returns: title of Note

        """
        return self.get_title()

    def __hash__(self):
        """ """
        return self.ident

    def get_contents(self):
        """Get the contents of the note. Includes header (front matter) and
        body.

        :return: contents of Note

        """
        return dumps(self.contents)

    def get_body(self):
        """Get the body of the note.

        :returns: body of Note (as-is, no parsing)

        """
        return self.contents.content

    def get_id(self):
        """Get the unique identifier for the Note.

        :returns: unique identifier

        """
        return self.ident

    def get_filename(self):
        """Get filename on disk for the Note.

        :returns: filename

        """
        return self.filename

    def get_tag(self, tag):
        """Get a tag by name from the Note. YAML is (kinda) used for Note
        structure, but not entirely to simplify editing of Notes.

        :tag: tag name of value to retrieve
        :returns: value for tag

        """
        if tag not in self.contents:
            raise ValueError('Tag "{t}" not found ({i})'.format(t=tag,
                             i=self.get_id()))
        return self.contents[tag]

    def get_tags(self):
        """Get all tags associated with the note.

        :returns: list of tags

        """
        if 'tags' not in self.contents:
            return []
        return self.contents['tags']

    def get_cdate(self):
        """Get the creation date of the Note.

        :returns: cdate

        """
        return date.fromisoformat(self.get_tag('date').split('T')[0])

    def get_mdate(self):
        """Get the modification date of the Note. This uses the mtime attribute
        of the file, which may change if the file has been copied previously.

        :returns: mdate

        """
        filename = Path(self.filename)
        return date.fromtimestamp(filename.stat().st_mtime)

    def get_title(self):
        """Get the title of the Note. Title is stored as a tag in the header.

        :returns: title

        """
        return self.get_tag('title')

    def get_links(self):
        """Get all outgoing Markdown links. Zettelkasten uses these links to
        create edges in the directed graph.

        :returns: list of tuple (link_name, link_target)

        """
        text, href, internal_link = '', '', False
        # Only process children of inline tokens
        for c in [t.children for t in self.T if t.type == 'inline']:
            for t in c:
                if t.type == 'link_open':
                    try:
                        href = int(t.attrs[t.attrIndex('target')][1])
                        internal_link = True
                    except ValueError:
                        # Special case: not an internal link
                        internal_link = False
                if t.type == 'text':
                    text = t.content
                if t.type == 'link_close' and internal_link:
                    yield((text, href))

    def get_word_count(self):
        """ Quick & dirty way to get word count """
        return len(self.get_body().split())

    def is_entry(self):
        """Is this Note an entry Note into the Zettelkasten?
        :returns: True if Note is an entry note, False when not

        """
        try:
            return bool(self.get_tag('entry'))
        except ValueError:
            return False

    def is_hidden(self):
        """ """
        try:
            return bool(self.get_tag('hide'))
        except ValueError:
            return False

    def to_html(self):
        """Render the body of the note to an HTML file.

        :returns: HTML representation for the Note.

        """
        return Note.render('note.html.tpl', title=self.get_title(),
                           display_id=self.display_id, ident=self.get_id(),
                           content=self.md.render(self.get_body()))

    @staticmethod
    def render(template, template_dir='templates/', **kwargs):
        """ Render the provided template """
        if Note._env is None:
            Note._env = Environment(loader=PackageLoader('thedudeabides',
                                    template_dir), trim_blocks=True)

            # Add custom filters
            def format_note(n, b, exit_notes=None):
                flag = ''
                if exit_notes is not None and n.get_id() in exit_notes:
                    flag = 'Ω '
                return f'|{"%02d" % b}| {flag}[{n.get_title()}]({n.get_id()})'
            Note._env.filters['format_note'] = format_note

        # Render the template
        return Note._env.get_template(template).render(**kwargs)
