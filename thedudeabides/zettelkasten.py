# -*- coding: utf-8 -*-

from .note import Note

from graph_tools import Graph
from os import walk
from os.path import join, splitext, isdir
# from pprint import pprint
from datetime import datetime
from jinja2 import Environment
from itertools import groupby
from operator import itemgetter

import logging
log = logging.getLogger(__name__)

ATTR_NOTE = 'note'
EXT_NOTE = 'md'


NOTE_NEW = """---
title: "{{ title }}"
date: "{{ date }}"
---

{{ body }}
"""

NOTE_REFS = """{{ contents }}
{% if notes_to|length > 0  or notes_from %}
## Ref.
{% endif %}

{% for b, note in notes_to %}
* |{{ '%02d' % b }}| [{{ note }}]({{ note.get_id() }})
{% endfor %}

{% if notes_from %}
---
{% for b, note in notes_from %}
* |{{ '%02d' % b }}| [{{ note }}]({{ note.get_id() }})
{% if (ident, note.get_id()) in notes_path %}
[{% for p in notes_path[(ident, note.get_id())] %}
[{{ loop.index }}](?note={{ p|join('&amp;note=') }}){% if not loop.last %}, {% endif %}
{% endfor %}]
{% endif %}
{% endfor %}

{% endif %}
""" # noqa

NOTE_INDEX = """---
title: "Index"
date: "{{ date }}"
---

* |xx| [Register](register.html)
---
{% for b, note in top_notes %}
* |{{ '%02d' % b }}| [{{ note }}]({{ note.get_id() }})
{% endfor %}

# 0. Ingang

{% for b, note in entry_notes %}
{{ loop.index }}. |{{ '%02d' % b }}| [{{ note }}]({{ note.get_id() }})
{% endfor %}

# 0. Inbox

{% for b, note in inbox_notes %}
* |{{ '%02d' % b }}| [{{ note }}]({{ note.get_id() }})
{% endfor %}
"""

NOTE_COLLECTED = """{% for note in notes %}
# {{ note.get_title() }} ({{ note.get_id() }})

{{ note.get_body() }}

{% endfor %}

"""

NOTE_REGISTER = """---
title: "Register"
date: "{{ date }}"
---

{% for k, v in notes %}

## {{ k }}

{% for note, ref in v %}
* [{{ note.get_title() }}]({{ note.get_id() }}) {%+ for n in ref %}
[{{ n.get_id() }}]({{ n.get_id() }}.html){% if not loop.last %}, {% endif %}
{% endfor %}

{% endfor %}
{% endfor %}

""" # noqa


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
        if not isdir(zettelkasten):
            raise ValueError('Invalid Zettelkasten directory provided')
        self.zettelkasten = zettelkasten
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

    def get_notes_to(self, v):
        """Get all Notes that refer to Note v.

        :v: ID of Note
        :returns: TODO

        """
        if not self.exists(v):
            raise ValueError('No Note for ID: "{v}" found'.format(v=v))
        # Get Notes for all incoming vertices
        g = self.get_graph()
        edges_to = set([i for l in g.edges_to(v) for i in l])
        n = [(len(g.edges_to(u)), self.get_note(u)) for u in edges_to if
             u is not v]
        return sorted(n, key=lambda x: x[0], reverse=True)

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
        hidden = []
        for u in self.g.vertices():
            # Get all outgoing links from this Note
            note = self.g.get_vertex_attribute(u, ATTR_NOTE)
            if note.is_hidden():
                hidden.append(note.get_id())
            for text, v in note.get_links():
                if not self.g.has_vertex(v):
                    log.error('Invalid link {v} in note {u}'.format(u=u, v=v))
                    continue
                # Add an edge from this Note to each referenced Note
                if not self.g.has_edge(u, v):
                    self.g.add_edge(u, v)
                    log.debug('Add edge from {u} to {v}'.format(u=u, v=v))

        # Remove the train of thought for any hidden notes
        for v in hidden:
            log.info('Delete hidden vertex "{v}"'.format(v=v))
            self.g.delete_vertices([n.get_id() for n in
                                    self._train_of_thought(v)])

        # Return the populated graph
        return self.g

    def is_entry_note(self, v):
        """True if the note is an entry note. Possible enhancement: use
        Note::is_entry() to check if the user has set the note as an entry
        notes.

        """
        if not self.exists(v):
            raise ValueError('No Note for ID: "{v}" found'.format(v=v))
        g = self.get_graph()
        return (len(g.edges_from(v)) == 0) and (len(g.edges_to(v)) != 0)

    def create_note(self, title='', body=''):
        """Create a new Note using a template. Does not write the note to disk.

        :title: title for note
        :body: body for note
        :returns: Note

        """
        env = Environment(trim_blocks=True).from_string(NOTE_NEW)
        contents = env.render(title=title, date=datetime.utcnow().isoformat(),
                              body=body)
        # Create Note
        g = self.get_graph()
        n = g.vertices()
        # Get largest Note ID, increment by 1
        v = max(n) + 1 if len(n) > 0 else 1
        # Compose filename
        filename = join(self.zettelkasten, '{v}.{e}'.format(v=v, e=EXT_NOTE))
        note = Note(v, filename, contents)
        # Add note to graph, so Zettelkasten::exists() works
        g.add_vertex(v)
        g.set_vertex_attribute(v, ATTR_NOTE, note)
        return note

    def exists(self, v):
        """Check if a Note with the provided id exists in the graph.

        :v: id of Note to retrieve
        :returns: True if Note exists, False if not

        """
        g = self.get_graph()
        return g.has_vertex(v)

    def _top_notes(self):
        """ """
        g = self.get_graph()
        # Get a top 10 of most referred notes
        notes = sorted([(len(g.edges_to(v)), self.get_note(v)) for v in
                        g.vertices()], key=lambda x: x[0], reverse=True)[:10]
        return notes

    def _entry_notes(self):
        """Get a list of entry notes. Entry notes have no outgoing edges, which
        makes them the starting point for a train of thought by following the
        back links.

        :returns: list of tuple(Notes, {b, Note})

        """
        g = self.get_graph()
        entry_notes = []
        entry_notes_to = {}
        exit_notes = [v for v in g.vertices() if len(g.edges_to(v)) == 0]
        exit_notes_from = {}
        exit_notes_path = {}
        for v in [v for v in g.vertices() if self.is_entry_note(v)]:
            entry_notes.append((len(g.edges_to(v)), self.get_note(v)))
            entry_notes_to[v] = self.get_notes_to(v)
            for u in exit_notes:
                if not g.is_reachable(u, v):
                    continue

                shortest_paths = []
                for p in g.shortest_paths(u, v):
                    if len(p) <= 2:
                        continue
                    shortest_paths.append(['%2F{}.html'.format(s)
                                           for s in p[::-1]])
                if len(shortest_paths) > 0:
                    exit_notes_path[(v, u)] = shortest_paths

                if v not in exit_notes_from:
                    exit_notes_from[v] = []

                # Only add exit notes which have a shortest path
                if (v, u) in exit_notes_path:
                    exit_notes_from[v].append((len(g.edges_from(u)),
                                               self.get_note(u)))
            exit_notes_from[v] = sorted(exit_notes_from[v], key=lambda x: x[0],
                                        reverse=True)
        return(sorted(entry_notes, key=lambda x: x[0], reverse=True),
               entry_notes_to, exit_notes_from, exit_notes_path)

    def _inbox(self):
        """Any Notes not part of a path between entry and exit are considered
        orphaned. These Notes need additional work to become integrated into
        the Zettelkasten. """
        g = self.get_graph()
        orphaned = set(g.vertices())
        #
        entry_notes, _, _, _ = self._entry_notes()
        for b, note in entry_notes:
            for n in self._train_of_thought(note.get_id()):
                if n.get_id() in orphaned:
                    orphaned.remove(n.get_id())
        orphaned = [(len(g.edges_from(v)), self.get_note(v)) for v in orphaned]
        return(sorted(orphaned, key=lambda x: x[0], reverse=True))

    def index(self):
        """Create a markdown representation of the index of notes.

        :returns: Note

        """
        entry_notes, entry_notes_to, exit_notes_from, _ = self._entry_notes()

        env = Environment(trim_blocks=True).from_string(NOTE_INDEX)
        return Note(0, contents=env.render(entry_notes=entry_notes,
                    entry_notes_to=entry_notes_to,
                    exit_notes_from=exit_notes_from,
                    inbox_notes=self._inbox(),
                    top_notes=self._top_notes(),
                    date=datetime.utcnow().isoformat()))

    def _collect(self, v):
        """Collect all Notes associated with the provided ID. All edges are
        traversed and the associated Notes are returned.

        :v: id of Note to use as starting point
        :returns: generator of Note

        """
        if not self.exists(v):
            raise ValueError('No Note for ID: "{v}" found'.format(v=v))
        g = self.get_graph()
        # Get network of related Notes
        explored = g.explore(v)
        log.info('Retrieved notes: {n}'.format(
                 n=', '.join(map(str, explored))))
        for v in explored:
            yield(g.get_vertex_attribute(v, ATTR_NOTE))

    def collect(self, v):
        """Collect all Notes associated with the provided ID.

        :v: id of Note to use as starting point
        :returns: Note for all collected notes

        """
        env = Environment(trim_blocks=True).from_string(NOTE_COLLECTED)
        return self.create_note(self.get_note(v).get_title(),
                                env.render(notes=self._collect(v)))

    def _register(self):
        """TODO: Docstring for _all.

        :returns: Dictionary of notes sorted by first letter

        """
        g = self.get_graph()
        # Get all notes and sort by first letter
        notes = []
        for v in g.vertices():
            ref = [self.get_note(u) for u in [u[0] for u in g.edges_to(v)]]
            notes.append((self.get_note(v).get_title()[0].upper(),
                         (self.get_note(v), ref)))
        notes = sorted(notes, key=itemgetter(0))
        # Group all notes by first letter
        for k, group in groupby(notes, key=itemgetter(0)):
            yield((k, [x[1] for x in sorted(group,
                  key=lambda n: n[1][0].get_title())]))

    def register(self):
        """TODO: Docstring for all.

        :returns: TODO

        """
        env = Environment(trim_blocks=True).from_string(NOTE_REGISTER)
        note = Note(0, 'Register', env.render(notes=self._register(),
                    date=datetime.utcnow().isoformat()))
        print(note.get_body())
        return(note)

    def _train_of_thought(self, s):
        """Find a "train of thought", starting at the note with the provided
        id.  Finds the shortest path to a leaf and returns the Notes, ordered
        by distance from the starting Note.

        :v: id of Note to use as starting point
        :returns: generator of Note

        """
        if not self.exists(s):
            raise ValueError('No Note for ID: "{v}" found'.format(v=s))

        explored = []
        need_visit = set()
        need_visit.add(s)
        g = self.get_graph()
        while need_visit:
            u = need_visit.pop()
            explored.append(u)
            for v in [i for l in g.edges_to(u) for i in l]:
                if v not in explored:
                    log.debug('Processing "{v}" in context of "{u}"'.format(
                              v=v, u=u))
                    need_visit.add(v)
        log.info('Retrieved notes: {n}'.format(
                 n=', '.join(map(str, explored))))
        for u in explored:
            yield(self.get_note(u))

    def train_of_thought(self, v):
        """Find a "train of thought".

        :v: id of Note to use as starting point
        :returns: Note for all collected notes

        """
        env = Environment(trim_blocks=True).from_string(NOTE_COLLECTED)
        return self.create_note(self.get_note(v).get_title(),
                                env.render(notes=self._train_of_thought(v)))

    def render(self):
        """Get all Notes in the Zettelkasten, including a list of referring
        Notes for each Note.

        :output: output directory, must exist

        """
        g = self.get_graph()
        _, _, exit_notes_from, exit_notes_path = self._entry_notes()
        # Write all Notes to disk
        for n in [self.get_note(v) for v in g.vertices()]:
            notes_from = None
            if self.is_entry_note(n.get_id()):
                notes_from = exit_notes_from[n.get_id()]
            # Render HTML template as a new Note
            env = Environment(trim_blocks=True).from_string(NOTE_REFS)
            note = Note(n.get_id(), contents=env.render(
                        ident=n.get_id(),
                        contents=n.get_contents(),
                        notes_to=self.get_notes_to(n.get_id()),
                        notes_from=notes_from,
                        notes_path=exit_notes_path))
            yield(note)
