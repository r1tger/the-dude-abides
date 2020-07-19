# -*- coding: utf-8 -*-

from .note import Note

from graph_tools import Graph
from os import walk
from os.path import join, splitext, expanduser, isdir

import logging
log = logging.getLogger(__name__)

ATTR_NOTE = 'note'
EXT_NOTE = 'md'


class Zettelkasten(object):

    """This class acts as the container for all notes in the Zettelkasten.
    Methods to work with the notes and associated graph are provided. This
    class mostly provides callers with generators to requested information
    about the Zettelkasten or contained notes.
    """

    def __init__(self, zettelkasten):
        """Constructor.

        :zettelkasten: pathname of directory where the notes are stored

        """
        self.zettelkasten = expanduser(zettelkasten)
        if not isdir(self.zettelkasten):
            raise ValueError('Invalid Zettelkasten directory provided')
        self.g = None

    def get_note(self, v):
        """Get a single Note instance by id.

        :v: id of Note to retrieve
        :returns: Note

        """
        if not self.exists(v):
            raise ValueError('No Note for ID: "{v}" found'.format(v=v))
        g = self.get_graph()
        return g.get_vertex_attribute(v, ATTR_NOTE)

    def get_notes(self):
        """Get all available Notes from the directory.

        :returns: generator of tuple (id, Note)

        """
        for root, dirs, files in walk(self.zettelkasten):
            for name in sorted(files):
                try:
                    # Skip filenames which do not contain an int
                    v = int(splitext(name)[0])
                except ValueError:
                    continue
                yield((v, Note(v, join(root, name))))

    def get_graph(self):
        """Create a directed graph, using each Note as a vertex and the
        Markdown links between Notes as edges. The graph is used to find
        clusters of Notes and to create a visual representation of the
        Zettelkasten.

        The excellent "graph-tools" library is used to create the directed
        graph.

        :returns: Graph containing all Notes in the Zettelkasten

        """
        # Cached version available?
        if self.g is not None:
            return self.g

        # Add all available Notes to the graph
        self.g = Graph(directed=True)

        # Get all Notes
        for v, note in self.get_notes():
            # Create a new vertex for each Note
            self.g.add_vertex(v)
            self.g.set_vertex_attribute(v, ATTR_NOTE, note)

        # Once all Notes have been add, add edges
        for u in self.g.vertices():
            # Get all outgoing links from this Note
            note = self.g.get_vertex_attribute(u, ATTR_NOTE)
            for text, v in note.get_links():
                if not self.g.has_vertex(v):
                    log.error('Invalid link {v} in note {u}'.format(u=u, v=v))
                    continue

                # Add an edge from this Note to each referenced Note
                if not self.g.has_edge(u, v):
                    self.g.add_edge(u, v)
                    log.debug('Add edge from {u} to {v}'.format(u=u, v=v))
        # Return the populated graph
        return self.g

    def registry(self):
        """Get a list of all Notes, sorted by outgoing edges (most edges
        first). Notes which link to (lots of) other Notes tend to summarise the
        Notes linked too, and are of interest when looking for clusters of
        information.

        :returns: generator of tuple (count, Note)

        """
        g = self.get_graph()
        vertices = [(len(g.edges_from(v)), v) for v in g.vertices()]
        for c, v in sorted(vertices, key=lambda x: x[0], reverse=True):
            yield((c, g.get_vertex_attribute(v, ATTR_NOTE)))

    def get_next_note(self):
        """Create a Note for the next available ID. The Note can be used to
        create new files in the Zettelkasten directory.

        :returns: Note

        """
        n = list(self.get_notes())
        # Get largest Note ID, increment by 1
        v = max([v for v, filename in n]) + 1 if len(n) > 0 else 1
        # Compose filename
        filename = join(self.zettelkasten, '{v}.{e}'.format(v=v, e=EXT_NOTE))
        return Note(v, filename)

    def exists(self, v):
        """Check if a Note with the provided id exists in the graph.

        :v: id of Note to retrieve
        :returns: True if Note exists, False if not

        """
        g = self.get_graph()
        return g.has_vertex(v)

    def inbox(self):
        """Get all unlinked notes (no associated edges). Unlinked notes should
        be processed and put in context of other notes in the Zettelkasten.

        :returns: generator of tuple (count, Note)

        """
        g = self.get_graph()
        vertices = [(len(g.edges_at(v)), v) for v in g.vertices()]
        for c, v in [(c, v) for c, v in vertices if c == 0]:
            yield((c, g.get_vertex_attribute(v, ATTR_NOTE)))

    def collect(self, v):
        """Collect all Notes associated with the provided id. All edges are
        traversed and the associated Notes are returned.

        :v: id of Note to use as starting point
        :returns: generator of Note

        """
        if not self.exists(v):
            raise ValueError('No Note for ID: "{v}" found'.format(v=v))
        g = self.get_graph()
        # Get network of related Notes
        for v in g.explore(v):
            yield(g.get_vertex_attribute(v, ATTR_NOTE))

    def train_of_thought(self, v):
        """Find a "train of thought", starting a the note with the provided id.
        Finds the shortest path to a leaf and returns the Notes, ordered by
        distance from the starting Note.

        :v: id of Note to use as starting point
        :returns: generator of tuple (distance, Note)

        """
        if not self.exists(v):
            raise ValueError('No Note for ID: "{v}" found'.format(v=v))
        g = self.get_graph()
        # Get network of related Notes
        dist, prev = g.dijkstra(v)
        for u, h in sorted(dist.items(), key=lambda x: x[1], reverse=True):
            yield((h, g.get_vertex_attribute(u, ATTR_NOTE)))

    def find(self, s):
        """Search for all notes containing term s.

        :s: search term
        :returns: generator of Note

        """
        g = self.get_graph()
        # Get all vertices
        for v in g.vertices():
            note = g.get_vertex_attribute(v, ATTR_NOTE)
            if note.find(s):
                yield(note)
