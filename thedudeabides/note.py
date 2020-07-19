# -*- coding: utf-8 -*-

from ngram import NGram
import re
from reparser import Parser, Token, MatchGroup

import logging
log = logging.getLogger(__name__)


class Note(object):

    """Encapsulate a Markdown file on disk. Note is usually created by
    Zettelkasten. A Note provides common operations for Notes.

    """

    boundary_chars = r'\s`!()\[\]{{}};:\'".,<>?«»“”‘’*_~='
    b_left = r'(?:(?<=[' + boundary_chars + r'])|(?<=^))'  # Lookbehind
    b_right = r'(?:(?=[' + boundary_chars + r'])|(?=$))'   # Lookahead

    markdown_start = b_left + r'(?<!\\){tag}(?!\s)(?!{tag})'
    markdown_end = r'(?<!{tag})(?<!\s)(?<!\\){tag}' + b_right
    markdown_link = r'(?<!\\)\[(?P<link>.+?)\]\((?P<url>.+?)\)'
    newline = r'\n|\r\n'

    def __init__(self, ident, filename):
        """Constructor.

        :ident: unique identifier for the Note
        :filename: filename of Note file. Can be relative or absolute

        """
        self.ident = ident
        self.filename = filename
        self.contents = None

    def parse(self):
        """Parse the Note contents for Markdown syntax. Mainly used to find
        links to other Notes, but can provide more information if needed in the
        future.

        :returns: generator of Segment

        """
        tokens = [
            Token('bi1',  *Note.markdown(r'\*\*\*'), is_bold=True,
                  is_italic=True),
            Token('bi2',  *Note.markdown(r'___'),    is_bold=True,
                  is_italic=True),
            Token('b1',   *Note.markdown(r'\*\*'),   is_bold=True),
            Token('b2',   *Note.markdown(r'__'),     is_bold=True),
            Token('i1',   *Note.markdown(r'\*'),     is_italic=True),
            Token('i2',   *Note.markdown(r'_'),      is_italic=True),
            Token('pre3', *Note.markdown(r'```'),    skip=True),
            Token('pre2', *Note.markdown(r'``'),     skip=True),
            Token('pre1', *Note.markdown(r'`'),      skip=True),
            Token('s',    *Note.markdown(r'~~'),     is_strikethrough=True),
            Token('u',    *Note.markdown(r'=='),     is_underline=True),
            Token('link', Note.markdown_link, text=MatchGroup('link'),
                  link_target=MatchGroup('url')),
            Token('br', Note.newline, text='\n', segment_type="LINE_BREAK")
        ]
        # Parse the contents of the note
        parser = Parser(tokens)
        return parser.parse(self.get_body())

    def __eq__(self, other):
        """Compare Note instances by unique identifier.

        """
        return self.ident == other

    def __repr__(self):
        """Return the Note title if cast to string().

        :returns: title of Note

        """
        return self.get_title()

    def get_body(self):
        """Get the body of the note. A later addition may be to distinguish
        between body and header, but YAML parsing needs to be sorted out first.
        See Note::get_tag() for more information.

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
        structure, but not entirely to simplify editing of Notes. Tags are
        supported, but parsed in a _very_ lazy manner.

        :tag: tag name of value to retrieve
        :returns: value for tag

        """
        tag = '{t}: '.format(t=tag)
        for t in [s.text for s in self.parse()]:
            # Lazy parsing: find first match for tag and return without quotes
            if t.startswith(tag):
                return t.split(tag)[1][1:-1]

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
        text = self.parse()
        # pprint([(segment.text, segment.params) for segment in text])
        links = [(x.text, int(x.params['link_target'])) for x in text
                 if 'link_target' in x.params]
        return links

    def find(self, s):
        """Search for a specific term in the text of the note. Performs a fuzzy
        match on the body of the Note.

        :s: search term
        :returns: True if s is found in Note, False if not

        """
        n = NGram(self.get_body().split(), key=lambda x: x.lower())
        # Try to match term s with a similarity of 0.5
        return True if n.find(s.lower(), 0.5) is not None else False

    @staticmethod
    def markdown(tag):
        """Return sequence of start and end regex patterns for simple Markdown
           tag

        """
        return (Note.markdown_start.format(tag=tag),
                Note.markdown_end.format(tag=tag))

    @staticmethod
    def url_complete(url):
        """If URL doesn't start with protocol, prepend it with http://

        """
        url_proto_regex = re.compile(r'(?i)^[a-z][\w-]+:/{1,3}')
        return url if url_proto_regex.search(url) else 'http://' + url
