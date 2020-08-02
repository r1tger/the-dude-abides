# -*- coding: utf-8 -*-

from ngram import NGram
from yaml import load, FullLoader
from jinja2 import Environment

from markdown_it import MarkdownIt
from markdown_it.token import nest_tokens
from markdown_it.extensions.front_matter import front_matter_plugin

import logging
log = logging.getLogger(__name__)

HTML = """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8"/>
        <title>{{ title }}</title>
        <link rel="stylesheet" href="main.css"/>
        <link href="/favicon.ico" rel="shortcut icon"/>
        <meta name="description" content="{{ title }}"/>
        <!--[if IE]>
        <script
            src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
        <![endif]-->
    </head>
    <body class="index">
        <section class="index-content">
            <h1>{{ title }}</h1>
            {{ content }}
        </section>
        <footer>
            <a href="index.html">Index</a>
        </footer>
    </body>
</html>
"""


class Note(object):

    """Encapsulate a Markdown file on disk. Note is usually created by
    Zettelkasten. A Note provides common operations for Notes.

    """

    def __init__(self, ident, filename=None, source=None):
        """Constructor.

        :ident: unique identifier for the Note
        :filename: filename of Note file. Can be relative or absolute
        :source: contents for Note. If not provided, filename is loaded on
                 first use

        """
        self.ident = ident
        self.filename = filename
        self.contents = source
        self.front_matter = None

        def render_link_open(self, tokens, idx, options, env):
            """Change any links to include '.html'. """
            ai = tokens[idx].attrIndex('target')
            target = '{t}.html'.format(t=tokens[idx].attrs[ai][1])
            tokens[idx].attrs[ai][1] = target
            return self.renderToken(tokens, idx, options, env)

        # Parse the contents of the note
        self.md = (MarkdownIt('commonmark').use(front_matter_plugin))
        self.md.add_render_rule('link_open', render_link_open)
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

    def get_body(self):
        """Get the body of the note. See Note::get_tag() for more information.

        :returns: body of Note (as-is, no parsing)

        """
        if self.contents is None:
            # Load the note as a YAML file
            with open(self.filename) as f:
                self.contents = f.read()
        return self.contents

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
        if self.front_matter is None:
            try:
                fm = [t for t in self.T if t.type == 'front_matter'][0]
                # Load front matter as YAML syntax
                self.front_matter = load(fm.content, Loader=FullLoader)
            except IndexError:
                self.front_matter = {}
        if tag not in self.front_matter:
            raise ValueError('Tag "{t}" not found'.format(t=tag))
        return self.front_matter[tag]

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
        text, href = '', ''
        # Only process children of inline tokens
        for c in [t.children for t in self.T if t.type == 'inline']:
            for t in c:
                if t.type == 'link_open':
                    href = int(t.attrs[0][1])
                    # href = int(t.attrIndex('target'))
                if t.type == 'text':
                    text = t.content
                if t.type == 'link_close':
                    yield((text, href))

    def render(self):
        """Render the note to an HTML file.

        :returns: HTML representation for the Note.

        """
        env = Environment().from_string(HTML)
        return env.render(title=self.get_title(),
                          content=self.md.render(self.get_body()))

    def find(self, s):
        """Search for a specific term in the text of the note. Performs a fuzzy
        match on the body of the Note.

        :s: search term
        :returns: True if s is found in Note, False if not

        """
        n = NGram(self.get_body().split(), key=lambda x: x.lower())
        # Try to match term s with a similarity of 0.5
        return True if n.find(s.lower(), 0.5) is not None else False
