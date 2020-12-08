# -*- coding: utf-8 -*-

from .note import Note

import networkx as nx
from os import walk
from os.path import join, splitext, isdir
# from pprint import pprint
from datetime import datetime
from jinja2 import Environment
from itertools import groupby
from operator import itemgetter
from statistics import mean

import logging
log = logging.getLogger(__name__)

EXT_NOTE = 'md'

NOTE_ID = 'ident'

NOTE_NEW = """---
title: "{{ title }}"
date: "{{ date }}"
---

{{ body }}
"""

NOTE_REFS = """{{ contents }}
{% if notes_to|length > 0 %}
## Ref.

{% for b, note, paths in notes_to %}
* |{{ '%02d' % b }}| [{{ note }}]({{ note.get_id() }})
{% for path in paths %}
{% if path|length > 2 %}
[[{{ loop.index }}](?note={{ path|join('&amp;note=') }})]{% if not loop.last %}, {% endif %}

{% endif %}
{% endfor %}
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

# Ingang

{% for b, note in entry_notes %}
{{ loop.index }}. |{{ '%02d' % b }}| [{{ note }}]({{ note.get_id() }})
{% endfor %}

"""

NOTE_COLLECTED = """{% for note in notes %}
## {{ note.get_id() }}. {{ note.get_title() }}

{{ note.get_body() | replace('# ', '## ') }}

{% endfor %}

"""

NOTE_REGISTER = """---
title: "Register"
date: "{{ date }}"
---

{% if stats %}
|Notities           |Totaal                 |Gemiddeld                 |
|:------------------|----------------------:|-------------------------:|
|Notities           |{{ stats.nr_vertices }}|n.v.t.                    |
|Relaties           |{{ stats.nr_edges }}   |{{ stats.avg_edges }}     |
|Minst verbonden    |{{ stats.min_edges }}  |n.v.t.                    |
|Meest verbonden    |{{ stats.max_edges }}  |n.v.t.                    |
|Aantal woorden     |{{ stats.word_count }} |{{ stats.avg_word_count }}|
|Ingangnotities     |{{ stats.nr_entry }}   |{{ stats.nr_entry_perc }}%|
|Uitgangnotities (Ω)|{{ stats.nr_exit }}    |{{ stats.nr_exit_perc }}% |
{% endif %}

{% for k, v in notes %}

## {{ k }}

{% for _, b, note, ref in v %}
* |{{ '%02d' % b }}| {%if note.get_id() in entry_notes %}Α {% endif %}
{%if note.get_id() in exit_notes %}Ω {% endif %}
[{{ note.get_title() }}]({{ note.get_id() }})
{% for n in ref %}
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
        self.G = None

    def get_note(self, v):
        """Get a single Note instance by id.

        :v: id of Note to retrieve
        :returns: Note

        """
        if not self.exists(v):
            raise ValueError('No Note for ID: "{v}" found'.format(v=v))
        # Filter by ident attribute
        g = self.get_graph()
        return [n for n, d in g.nodes(data=True) if d[NOTE_ID] == v].pop()

    def get_notes(self):
        """Get all available Notes from the directory.

        :returns: generator of tuple (id, Note)

        """
        # Process all Notes in Zettelkasten
        for root, dirs, files in walk(self.zettelkasten):
            for name in sorted(files):
                try:
                    # Skip filenames which do not contain an int
                    v = int(splitext(name)[0])
                except ValueError:
                    continue
                yield(Note(v, join(root, name)))

    def get_notes_to(self, s, t):
        """Get all Notes that refer to Note v. If list t is provided, paths are
        resolved between vertex v and each vertex listed in t. The result is
        added to the output.

        :s:
        :t:
        :returns: tuple of tuple (ref, Note), dictionary of paths

        """
        exit_notes = [v for _, v in self._exit_notes()]
        if s in exit_notes:
            return []
        G = self.get_graph()
        # Add direct predecessors, if a predecessor is not an exit Note
        notes_to = [(G.out_degree(n), n, []) for n in G.predecessors(s)
                    if n not in exit_notes]
        for n in t:
            # If not path exists between the source and target, skip
            if not nx.has_path(G, n, s):
                continue
            # Add all paths to target notes
            paths = []
            for path in nx.all_shortest_paths(G, n, s, weight='weight'):
                # TODO: don't generate html filename here, use template
                paths.append(['%2F{}.html'.format(p.get_id())
                              for p in path[::-1]])
            notes_to.append((G.in_degree(n), n, paths))
        return sorted(notes_to, key=itemgetter(0), reverse=True)

    def get_filename(self, v):
        """Create a filename based on Note ID. """
        return(join(self.zettelkasten, '{v}.{e}'.format(v=v, e=EXT_NOTE)))

    def get_graph(self):
        """Create a directed graph, using each Note as a vertex and the
        Markdown links between Notes as edges. The graph is used to find
        clusters of Notes and to create a visual representation of the
        Zettelkasten.

        :returns: Graph containing all Notes in the Zettelkasten

        """
        # Cached version available?
        if self.G is not None:
            return self.G

        # Add all available Notes to the graph
        self.G = nx.DiGraph()
        self.G.add_nodes_from([(n, {NOTE_ID: n.get_id()})
                               for n in self.get_notes()])
        # Get all Notes
        for note in self.G.nodes():
            # Add edges
            for text, v in note.get_links():
                try:
                    self.G.add_edge(note, self.get_note(v))
                except ValueError as e:
                    log.error('While processing note "{v}": {e}'.format(e=e,
                              v=note.get_id()))
        # Update edges to combined in_degree as weight
        for s, t in self.G.edges():
            weight = self.G.in_degree(s) + self.G.in_degree(t)
            self.G.add_edge(s, t, weight=weight)
        # Delete hidden Notes and associated Notes
        notes = set()
        for n in [n for n in self.G.nodes() if n.is_hidden()]:
            notes |= set(self._train_of_thought(n))
        log.info('Deleted notes: "{n}"'.format(n='", "'.join(map(str, notes))))
        self.G.remove_nodes_from(notes)
        # Return the populated graph
        return self.G

    def get_stats(self):
        """ Get information about the Zettelkasten. """
        G = self.get_graph()
        stats = {}
        # Number of notes
        stats['nr_vertices'] = len(G.nodes())
        # Number of links between notes
        stats['nr_edges'] = len(G.edges())
        edges = [G.degree(n) for n in G.nodes()]
        stats['avg_edges'] = int(mean(edges))
        stats['min_edges'] = int(min(edges))
        stats['max_edges'] = int(max(edges))
        # Average word count
        wc = [n.get_word_count() for n in G.nodes()]
        stats['word_count'] = sum(wc)
        stats['avg_word_count'] = int(mean(wc))
        # Entry & exit notes
        stats['nr_entry'] = len(self._entry_notes())
        stats['nr_entry_perc'] = int((stats['nr_entry'] /
                                      stats['nr_vertices']) * 100)
        stats['nr_exit'] = len(self._exit_notes())
        stats['nr_exit_perc'] = int((stats['nr_exit'] /
                                     stats['nr_vertices']) * 100)
        # Statistics
        return stats

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
        G = self.get_graph()
        # Get largest Note ID, increment by 1
        n = max([d[NOTE_ID] for n, d in G.nodes(data=True)])
        v = (n + 1) if (n > 0) else 1
        # Compose filename
        return Note(v, self.get_filename(v), contents)

    def exists(self, v):
        """Check if a Note with the provided id exists in the graph.

        :v: id of Note to retrieve
        :returns: True if Note exists, False if not

        """
        G = self.get_graph()
        return G.has_node(v)

    def _top_notes(self):
        """ Get a top 10 of most referred notes. """
        G = self.get_graph()
        return self._get_notes(G.nodes())[:10]

    def _get_notes(self, nodes):
        """ Create a list of notes n for use in templates.

        :vertices: list of vertex IDs

        """
        G = self.get_graph()
        notes = [(G.in_degree(n), n) for n in nodes]
        return sorted(notes, key=itemgetter(0), reverse=True)

    def _exit_notes(self):
        """Get a list of exit notes. Exit notes have no incoming edges, which
        makes them the ending point for a train of thought.

        :returns: list of tuple(b, Note)

        """
        G = self.get_graph()
        return self._get_notes([v for v, d in G.in_degree() if d == 0])

    def _entry_notes(self):
        """Get a list of entry notes. Entry notes have no outgoing edges, which
        makes them the starting point for a train of thought by following the
        back links.

        :returns: list of tuple(b, Note)

        """
        G = self.get_graph()
        return self._get_notes([v for v, d in G.out_degree() if d == 0])

    def index(self):
        """Create a markdown representation of the index of notes.

        :returns: Note

        """
        env = Environment(trim_blocks=True).from_string(NOTE_INDEX)
        return Note(0, contents=env.render(entry_notes=self._entry_notes(),
                                           top_notes=self._top_notes(),
                                           date=datetime.utcnow().isoformat()),
                    display_id=False)

    def _collect(self, s):
        """Collect all Notes associated with the provided Note. All edges are
        traversed and the associated Notes are returned.

        :s: list of Notes to use as starting point
        :returns: generator of Note

        """
        notes = set(s)
        for note in s:
            notes |= set([n for n, _ in nx.bfs_predecessors(self.get_graph(),
                          source=note)])
        log.info('Found notes: "{n}"'.format(n='", "'.join(map(str, notes))))
        return notes

    def collect(self, v):
        """Collect all Notes associated with the provided ID.

        :v: tuple of Notes to use as starting point
        :returns: Note for all collected notes

        """
        env = Environment(trim_blocks=True).from_string(NOTE_COLLECTED)
        notes = [self.get_note(u) for u in v]
        return self.create_note(notes[0].get_title(),
                                env.render(notes=self._collect(notes)))

    def _register(self):
        """Collect all notes and group by first leter of note title.

        :returns: Dictionary of notes sorted by first letter

        """
        G = self.get_graph()
        # Get all notes and sort by first letter
        notes = sorted([(n.get_title()[0].upper(), G.in_degree(n), n,
                        list(G.predecessors(n))) for n in G.nodes()],
                       key=itemgetter(0))
        # Group all notes by first letter, yield each group
        for k, group in groupby(notes, key=itemgetter(0)):
            yield((k, sorted(group, key=lambda x: x[2].get_title().upper())))

    def register(self):
        """Create a registry of all notes, sorted by first letter of note
        title.

        :returns Note with register

        """
        exit_notes = [n for b, n in self._exit_notes()]
        entry_notes = [n for b, n in self._entry_notes()]
        env = Environment(trim_blocks=True).from_string(NOTE_REGISTER)
        return Note(0, 'Register', env.render(notes=self._register(),
                    stats=self.get_stats(), exit_notes=exit_notes,
                    entry_notes=entry_notes,
                    date=datetime.utcnow().isoformat()),
                    display_id=False)

    def _train_of_thought(self, s):
        """Find a "train of thought", starting at the note with the provided
        id. Finds all notes from the starting point to any endpoints, by
        following backlinks.

        :s: Note to use as starting point
        :returns: generator of Note

        """
        explored = []
        need_visit = set()
        need_visit.add(s)
        G = self.get_graph()
        while need_visit:
            u = need_visit.pop()
            explored.append(u)
            for v in G.predecessors(u):
                if v not in explored:
                    log.debug('Processing "{v}" in context of "{u}"'.format(
                              v=v, u=u))
                    need_visit.add(v)
        for u in explored:
            yield(u)

    def train_of_thought(self, s):
        """Find a "train of thought".

        :s: id of Note to use as starting point
        :returns: Note for all collected notes

        """
        env = Environment(trim_blocks=True).from_string(NOTE_COLLECTED)
        source = self.get_note(s)
        notes = list(self._train_of_thought(source))
        log.info('Found notes: {n}'.format(n=', '.join(map(str, notes))))
        return self.create_note(source.get_title(), env.render(notes=notes))

    def render(self):
        """Get all Notes in the Zettelkasten, including a list of referring
        Notes for each Note.

        :output: output directory, must exist

        """
        G = self.get_graph()
        exit_notes = [u for b, u in self._exit_notes()]
        # Write all Notes to disk
        for n in G.nodes():
            notes_to = self.get_notes_to(n, exit_notes)
            # Render HTML template as a new Note
            env = Environment(trim_blocks=True).from_string(NOTE_REFS)
            note = Note(n.get_id(), contents=env.render(
                        ident=n.get_id(),
                        contents=n.get_contents(),
                        notes_to=notes_to))
            yield(note)
