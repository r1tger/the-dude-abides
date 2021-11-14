# -*- coding: utf-8 -*-

from .note import Note

import networkx as nx
from os import walk
from os.path import join, splitext, isdir
from datetime import datetime, date, timedelta
from itertools import groupby
from operator import itemgetter
from statistics import mean
from random import sample, shuffle
from pprint import pprint
from re import findall
from json import dumps

from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.wordcount import wordcount_plugin

import logging
log = logging.getLogger(__name__)

EXT_NOTE = 'md'
NOTE_ID = 'ident'
NOTE_MDATE = 'mdate'


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
        self.N = {}
        # Set up Markdown parser
        self.md = MarkdownIt('default').use(footnote_plugin).use(wordcount_plugin, store_text=True)
        self.md.add_render_rule('link_open', Zettelkasten.render_link_open)

    @staticmethod
    def render_link_open(instance, tokens, idx, options, env):
        """Change any links to include '.html'. """
        try:
            # If the target is an int, convert to point to an HTML file
            target = '{t}.html'.format(t=int(tokens[idx].attrs['href']))
            tokens[idx].attrs['href'] = target
        except ValueError:
            # Use target as-is (don't break other links)
            pass
        return instance.renderToken(tokens, idx, options, env)

    def get_note(self, v):
        """Get a single Note instance by id.

        :v: id of Note to retrieve
        :returns: Note

        """
        if not self.exists(v):
            raise ValueError(f'No Note for ID: "{v}" found')
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
                yield(Note(self.md, v, join(root, name)))

    def _get_path(self, s, t):
        """Find the shortest path between two vertices and create an HTML path.

        :s: source note
        :t: target note
        :returns: list of HTML filenames

        """
        G = self.get_graph()
        paths = []
        for path in nx.all_shortest_paths(G, s, t, weight='weight'):
            # TODO: don't generate html filename here, use template
            paths.append(['%2F{}.html'.format(p.get_id())
                          for p in path[::-1]])
        return paths

    def get_notes_from(self, v, entry_notes):
        """Create a lattice from any entry note that has a path to Note v. If
        multiple lattices are found, all lattices are displayed.

        :v: ID of Note to find lattices for
        :entry_notes: list of notes to resolve paths from
        :returns: Note containing lattices

        """
        s = self.get_note(v)
        G = self.get_graph()
        lattices = []
        for t in entry_notes:
            if not nx.has_path(G, s, t) or s is t:
                continue
            lattices.append((G.in_degree(t), t, self._get_path(s, t)))
        return sorted(lattices, key=itemgetter(0), reverse=True)

    def get_notes_to(self, s, exit_notes, entry_notes, no_random=False):
        """Get all Notes that refer to Note v. If list t is provided, paths are
        resolved between vertex v and each vertex listed in t. The result is
        added to the output.

        :s: note to retrieve referring notes for
        :exit_notes: list of notes to resolve paths to from note s
        :entry_notes: list of entry notes
        :returns: tuple of tuple (ref, Note), tuple (ref, Note, paths)

        """
        G = self.get_graph()
        notes_to = list(G.predecessors(s))
        lattices = []
        found = set()

        if not no_random:
            # Shuffle the exit notes to add an element of surprise
            shuffle(exit_notes)
        # for t in sorted(exit_notes, reverse=True):
        for t in exit_notes:
            if not nx.has_path(G, t, s) or t in notes_to or s is t:
                continue
            # Find all entry notes that have a path to t (cache result)
            if t not in self.N:
                self.N[t] = set([n for n in entry_notes
                                 if nx.has_path(G, t, n)])
            if len(self.N[t] - found) == 0:
                continue
            found |= self.N[t]
            # Add all paths to target notes
            lattices.append((G.in_degree(t), t, self._get_path(t, s)))
        return sorted(lattices, key=itemgetter(0), reverse=True)

    def _get_notes_date(self, days, attr=NOTE_MDATE):
        """ """
        G = self.get_graph()
        from_date = date.today() - timedelta(days=days)
        # Get all notes from specified data till now
        notes = [n for n, d in G.nodes(data=True) if d[attr] > from_date]
        return self._get_notes(notes)

    def get_filename(self, v):
        """Create a filename based on Note ID. """
        return(join(self.zettelkasten, f'{v}.{EXT_NOTE}'))

    def count(self):
        """ """
        G = self.get_graph()
        return len(G.nodes())

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
        self.G.add_nodes_from([(n, {NOTE_ID: n.get_id(),
                                    NOTE_MDATE: n.get_mdate()})
                               for n in self.get_notes()])
        # Get all Notes
        for note in self.G.nodes():
            # Add edges
            for text, v in note.get_links():
                try:
                    # Add edge, include link text for reference in register
                    self.G.add_edge(note, self.get_note(v), label=text)
                except ValueError as e:
                    log.error(f'While processing note "{note.get_id()}": {e}')
        # Update edges to combined in_degree as weight
        for s, t in self.G.edges():
            weight = self.G.in_degree(s) + self.G.in_degree(t)
            self.G.add_edge(s, t, weight=weight)
        # Delete hidden Notes and associated Notes
        notes = set()
        for n in [n for n in self.G.nodes() if n.is_hidden()]:
            notes |= set(self._explore(n, self.G.predecessors))
        log.debug('Deleted note: "{n}"'.format(n='", "'.join(map(str, notes))))
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
        G = self.get_graph()
        # Get largest Note ID, increment by 1
        notes = [d[NOTE_ID] for n, d in G.nodes(data=True)]
        v = max(notes) + 1 if len(notes) > 0 else 1
        # Compose Note
        contents = Note.render('new.md.tpl', title=title, body=body,
                               date=datetime.utcnow().isoformat())
        return Note(self.md, v, self.get_filename(v), contents)

    def exists(self, v):
        """Check if a Note with the provided id exists in the graph.

        :v: id of Note to retrieve
        :returns: True if Note exists, False if not

        """
        G = self.get_graph()
        return G.has_node(v)

    def _get_notes(self, nodes, sort=True):
        """Create a list of notes n for use in templates.

        :vertices: list of vertex IDs

        """
        G = self.get_graph()
        notes = [(G.in_degree(n), n) for n in nodes]
        return (sorted(notes, key=itemgetter(0), reverse=True)
                if sort else notes)

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
        n = [(n, G.in_degree(n), G.out_degree(n)) for n in G.nodes()]
        # Get all notes without outgoing links
        notes = set([note for note, in_degree, out_degree in n
                     if in_degree != 0 and out_degree == 0])
        # Add any note that is marked as an entry note
        notes |= set([v for v in G.nodes() if v.is_entry()])
        return self._get_notes(notes)

    def _inbox(self):
        """List of notes that have neither predecessors or successors.

        :returns: list of tuple(b, Note)

        """
        G = self.get_graph()
        notes = [(n, G.in_degree(n), G.out_degree(n)) for n in G.nodes()]
        return self._get_notes([note for note, in_degree, out_degree in notes
                                if in_degree == 0 and out_degree == 0])

    def inverted_index(self):
        """
        """
        G = self.get_graph()
        # Quick indexing on document level
        exclude = ['de', 'het', 'een', 'één', 'zijn', 'hebben', 'doen', 'naar',
                   'nemen', 'niet', 'omdat', 'over', 'tussen', 'onder', 'twee',
                   'vanuit', 'veel', 'volgende', 'voor', 'achter', 'wanneer',
                   'welke', 'worden', 'wordt', 'zelf', 'zich', 'zonder',
                   'andere']
        inverted_index = {}
        for n in G.nodes():
            # Tokenise body of Note
            plaintext = findall(r'\w+', n.get_plaintext())
            tokens = set([t.lower() for t in plaintext if len(t) > 3 and
                          t.lower() not in exclude])
            # Add to inverted index
            for t in tokens:
                if t not in inverted_index:
                    inverted_index[t] = []
                inverted_index[t].append(n)
        log.info(f'{len(inverted_index)} terms in inverted index')
        content = Note.render('search.html.tpl',
                              inverted_index=inverted_index,
                              date=datetime.utcnow().isoformat())
        return Note.render('note.html.tpl', title='Zoeken',
                           display_id=False, ident=0, content=content)

    def index(self):
        """Create a markdown representation of the index of notes.

        :returns: Note

        """
        exit_notes = [u for b, u in self._exit_notes()]
        contents = Note.render('index.md.tpl', title='Notities',
                               entry_notes=self._entry_notes(),
                               exit_notes=exit_notes,
                               inbox=self._inbox(),
                               date=datetime.utcnow().isoformat())
        return Note(self.md, 0, contents=contents, display_id=False)

    def _register(self):
        """Collect all notes and group by first leter of note title.

        :returns: Tuple of notes sorted by first letter

        """
        def get_predecessors(G, n):
            # Find all predecessors for a note by incoming edge
            p = [(u, data['label']) for u, v, data in G.in_edges(n, data=True)]
            return sorted(p, key=itemgetter(0))
        G = self.get_graph()
        # Get all notes and sort by first letter
        notes = sorted([(n.get_title()[0].upper(), G.in_degree(n), n,
                        get_predecessors(G, n)) for n in G.nodes()],
                       key=itemgetter(0))
        # Group all notes by first letter, yield each group
        for k, group in groupby(notes, key=itemgetter(0)):
            yield((k, sorted(group, key=lambda x: x[2].get_title().upper())))

    def register(self, days=3):
        """Create a registry of all notes, sorted by first letter of note
        title.

        :returns Note with register

        """
        exit_notes = [n for b, n in self._exit_notes()]
        entry_notes = [n for b, n in self._entry_notes()]
        contents = Note.render('register.md.tpl', notes=self._register(),
                               stats=self.get_stats(), exit_notes=exit_notes,
                               entry_notes=entry_notes,
                               recent_notes=self._get_notes_date(days),
                               date=datetime.utcnow().isoformat())
        return Note(self.md, 0, 'Register', contents=contents,
                    display_id=False)

    def _tags(self):
        """Collect all notes and group by tag.

        :returns: Tuple of tag, notes

        """
        G = self.get_graph()
        tags = {}
        for note in G.nodes():
            # Tag the note for each associated tag
            for tag in note.get_tags():
                if tag not in tags:
                    tags[tag] = []
                tags[tag].append(note)
        for k, v in tags.items():
            yield((k, self._get_notes(v)))

    def tags(self):
        """Create an overview of all tags, grouping notes by tag.

        :returns: Note with tags

        """
        contents = Note.render('tags.md.tpl', notes=self._tags(),
                               date=datetime.utcnow().isoformat())
        return Note(self.md, 0, 'Register', contents=contents,
                    display_id=False)

    def _explore(self, s, nodes, depth=None):
        """Find a "train of thought", starting at the note with the provided
        id. Finds all notes from the starting point to any endpoints, by
        following backlinks.

        :s: Note to use as starting point
        :nodes: Iterator to use to traverse the graph. See explore() for an
                example on how to use this
        :returns: generator of Note

        """
        explored = []
        need_visit = set()
        need_visit.add(s)
        while need_visit:
            u = need_visit.pop()
            explored.append(u)
            for v in nodes(u):
                if v not in explored:
                    need_visit.add(v)
        return explored

    def predecessors(self, s, depth=99):
        """Find a "train of thought" across all predecessors (parents).

        :s: id of Note to use as starting point
        :depth: radius of nodes from center to include
        :returns: Note for all collected notes

        """
        s = self.get_note(s)
        G = nx.ego_graph(self.get_graph().reverse(), s, depth, center=False)
        return self.create_note(s.get_title(), Note.render('collected.md.tpl',
                                notes=[s] + list(G)))

    def successors(self, s, depth=99):
        """Find a "train of thought" across all successors (children).

        :s: id of Note to use as starting point
        :depth: radius of nodes from center to include
        :returns: Note for all collected notes

        """
        s = self.get_note(s)
        G = nx.ego_graph(self.get_graph(), s, depth, center=False)
        return self.create_note(s.get_title(), Note.render('collected.md.tpl',
                                notes=[s] + list(G)))

    def _suggestions(self, days):
        """Generate a list of suggestions for recently modified notes.
        Suggested notes are not part of the (multiple) train of thought(s) the
        sampled notes are a part of.

        :days: number of days in the past to look for modified notes
        :returns: list((references, note), [suggested notes])

        :todo: a possible optimalisation is to limited the nodes for review to
               only include exit notes. This reduces the number of notes to
               check to ~30% of the number of notes in the Zettelkasten.
        """
        G = self.get_graph()
        suggestions = []
        for b, t in self._get_notes_date(days):
            # Find all entry notes that have a path to the sampled note
            entry_notes = [s for _, s in self._entry_notes()
                           if nx.has_path(G, t, s) and s is not t]
            review = list(G.nodes())
            for n in entry_notes:
                for s in G.nodes():
                    # Remove all notes that have a path to the entry note
                    if nx.has_path(G, s, n) and s in review:
                        review.remove(s)
            log.info('{t} has {x} candidates'.format(x=len(review), t=t))
            suggestions.append(((b, t), self._get_notes(sample(review, 3))))
        return suggestions

    def today(self, birthday, days=3):
        """Create an overview of today.

        :birthday: date with birthday
        :days: number of days in the past to look for modified notes
        :returns: Note containing an overview of today

        """
        t = date.today()
        # How many days have I been alive?
        days_from = (t - birthday).days
        # How many days until I reach next [age] milestone?
        age = t.year - birthday.year
        milestone = age if age % 10 == 0 else (age + 10) - (age % 10)
        next_birthday = birthday.replace(year=birthday.year + milestone)
        days_to = (next_birthday - t).days
        # Days since COVID started in NL
        days_covid = (t - date.fromisoformat('2020-02-27')).days
        # Days till [event]
        days_hh = (date.fromisoformat('2022-02-11') - t).days
        days_mch = (date.fromisoformat('2022-07-22') - t).days
        # Suggestions
        contents = Note.render('today.md.tpl', days_from=days_from,
                               days_to=days_to, milestone=milestone,
                               days_covid=days_covid, days_hh=days_hh,
                               days_mch=days_mch,
                               stats=self.get_stats(),
                               inbox=len(self._inbox()),
                               suggestions=self._suggestions(days), days=days,
                               entry_notes=self._entry_notes(),
                               date=datetime.utcnow().isoformat())
        return Note(self.md, 0, contents=contents, display_id=False)

    def lattice(self, v):
        """Create a lattice from any entry note that has a path to Note v. If
        multiple lattices are found, all lattices are displayed.

        :v: ID of Note to find lattices for
        :returns: Note containing lattices

        """
        s = self.get_note(v)
        G = self.get_graph()

        lattice = []
        for t in [t for _, t in self._entry_notes()]:
            if nx.has_path(G, s, t) and s is not t:
                path = self._get_notes(list(nx.all_shortest_paths(
                       G, s, t, weight='weight'))[0][::-1], False)
                lattice.append((t, path))
        contents = Note.render('lattice.md.tpl', source=s, lattice=lattice,
                               date=datetime.utcnow().isoformat())
        return Note(self.md, 0, contents=contents, display_id=False)

    def lint(self):
        """Perform some basic integrity checks on the Zettelkasten.
        """
        G = self.get_graph()
        edges = list(G.edges())
        # Find all duplicate relations
        d = [(s, t) for s, t in edges if (t, s) in edges]
        out = []
        for s, t in sorted(d, key=itemgetter(0)):
            if (t, s) in out or s.is_entry() or t.is_entry():
                continue
            log.info(f'{s.get_id()}. {s} -> {t.get_id()}. {t}')
            out.append((s, t))

    def render(self, no_random=False):
        """Get all Notes in the Zettelkasten, including a list of referring
        Notes for each Note.

        :output: output directory, must exist

        """
        G = self.get_graph()
        # exit_notes = sorted([u for _, u in self._exit_notes()], reverse=True)
        entry_notes = sorted([u for _, u in self._entry_notes()], reverse=True)
        exit_notes = sorted([u for _, u in self._exit_notes()], reverse=True)
        # Write all Notes to disk
        for n in G.nodes():
            notes_to = self._get_notes(G.predecessors(n))
            lattices_to = self.get_notes_to(n, exit_notes, entry_notes,
                                            no_random)
            lattices_from = self.get_notes_from(n, entry_notes)
            # Render contents with references as a new Note
            note = Note(self.md, n.get_id(), contents=Note.render(
                        'note.md.tpl', ident=n.get_id(),
                        contents=n.get_contents(), notes_to=notes_to,
                        lattices_to=lattices_to, lattices_from=lattices_from,
                        exit_notes=exit_notes))
            yield(note)

    def _get_vis_js(self, G, note, depth=1):
        """ """
        ego = nx.ego_graph(G, note, depth, undirected=True)
        nodes = []
        for node in ego.nodes():
            n = {'id': node.get_id(), 'title': node.get_title(),
                 'label': str(node.get_id()), 'value': G.in_degree(node)}
            if node == note:
                n['color'] = '#d81e05'
            nodes.append(n)
        edges = []
        for f, t in ego.edges():
            edges.append({'from': f.get_id(), 'to': t.get_id()})
        return (nodes, edges)

    def to_html(self, note):
        """Convert a Note to HTML.

        Creates all nodes and edges for vis-network.js:
            https://visjs.github.io/vis-network/docs/network/

        :note: Note to convert to HTML
        :returns: HTML content

        """
        G = self.get_graph()
        nodes, edges = self._get_vis_js(G, note)
        return Note.render('note.html.tpl', title=note.get_title(),
                           display_id=note.display_id, ident=note.get_id(),
                           nodes=dumps(nodes), edges=dumps(edges),
                           display_graph=True,
                           content=self.md.render(note.get_body()))
