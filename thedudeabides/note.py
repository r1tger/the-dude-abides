# -*- coding: utf-8 -*-

from jinja2 import Environment

from markdown_it import MarkdownIt
from markdown_it.token import nest_tokens
from frontmatter import load, loads, dumps

import logging
log = logging.getLogger(__name__)

HTML = """<!DOCTYPE html>
<html lang="nl">
    <head>
        <meta charset="UTF-8"/>
        <title>{{ title }}</title>
        <link rel="stylesheet" href="main.css"/>
        <link href="/favicon.ico" rel="shortcut icon"/>
        <style>
            @import url('http://fonts.googleapis.com/css?family=Open+Sans:400,700');
            @import url('http://fonts.googleapis.com/css?family=PT+Serif:400,400italic');
            html {
                min-height: 100%;
            }
            body {
                width: 80%;
                margin: auto;
                font-size: medium;
            }
            footer {
                border-top: 1px solid #d81e05;
                padding: 0.5em 0 0.5em 0;
            }
            a {
                color: #d81e05;
                font-family: 'Open Sans', sans-serif;
                line-height: 1.5em;
                text-decoration: none;
            }
            h1, h2, h3 {
                font-family: 'Open Sans', sans-serif;
                color: #d81e05;
            }
            h1 {
                border-bottom: 1px solid #d81e05;
                font-size: x-large;
            }
            h2 {
                font-size: large;
            }
            h3 {
                font-size: medium;
            }
            p, li {
                color: #404040;
                font-family: 'PT Serif', serif;
                line-height: 1.5em;
                text-align: justify;
                text-justify: auto;
            }
            img {
                clear: both;
                display: block;
                margin: 1em auto 1em auto;
                max-width: 100%;
                height: auto;
                border: 1px solid #404040;
            }
        </style>
        <meta name="description" content="{{ title|e }}"/>
        <!--[if IE]>
        <script
            src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
        <![endif]-->
    </head>
    <body class="index">
        <section class="index-content">
            <h1>{{ title|e }}</h1>
            {{ content }}
        </section>
        <footer>
            <a href="index.html">Index</a>
        </footer>
    </body>
</html>
"""    # noqa


class Note(object):

    """Encapsulate a Markdown file on disk. Note is usually created by
    Zettelkasten. A Note provides common operations for Notes.

    """

    def __init__(self, ident, filename=None, contents=None):
        """Constructor.

        :ident: unique identifier for the Note
        :filename: filename of Note file. Can be relative or absolute
        :contents: contents for Note. If not provided, filename is loaded on
                 first use

        """
        self.ident = ident
        self.filename = filename
        self.contents = load(filename) if contents is None else loads(contents)
        self.front_matter = None

        def render_link_open(self, tokens, idx, options, env):
            """Change any links to include '.html'. """
            ai = tokens[idx].attrIndex('target')
            try:
                # If the target is an int, convert to point to an HTML file
                target = '{t}.html'.format(t=int(tokens[idx].attrs[ai][1]))
                tokens[idx].attrs[ai][1] = target
            except ValueError:
                # Use target as-is (don't break other links)
                pass
            return self.renderToken(tokens, idx, options, env)

        # Parse the contents of the note
        self.md = MarkdownIt('commonmark')
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

    def get_contents(self):
        """Get the contents of the note. Includes header (front matter) and
        body.

        :return: contents of Note

        """
        return dumps(self.contents)

    def get_body(self):
        """Get the body of the note. See Note::get_tag() for more information.

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

    def render(self):
        """Render the note to an HTML file.

        :returns: HTML representation for the Note.

        """
        env = Environment().from_string(HTML)
        return env.render(title=self.get_title(),
                          content=self.md.render(self.get_body()))
