#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .zettelkasten import Zettelkasten

from argparse import ArgumentParser
from datetime import datetime
from os import environ
# from pprint import pprint
from subprocess import call, run
from sys import exit

import logging
log = logging.getLogger(__name__)

LOG_FORMAT = '[%(levelname)s] %(message)s'


def logger(options):
    """ """
    # Set up logging
    if options.log:
        handler = logging.FileHandler(options.log)
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    # Add handler to the root log
    logging.root.addHandler(handler)
    # Set log level
    level = logging.DEBUG if options.debug else logging.INFO
    logging.root.setLevel(level)


def parse():
    """Parse command line options.

    :returns: Namespace

    """
    parser = ArgumentParser()
    # Shared
    parser.add_argument('--debug', help='enable debug mode',
                        action='store_true', default=False)
    parser.add_argument('--log', help='log file')
    parser.add_argument('--zettelkasten', default='.',
                        help='directory containing the zettelkasten')
    parser.add_argument('-o', '--output', action='store_true', default=False,
                        help='Write the output to disk')
    # Note specific
    parser.add_argument('--create', action='store_true',
                        help='create a new note')
    parser.add_argument('-d', '--distance', type=int,
                        help='Maximum distance from source')
    parser.add_argument('-e', '--edit', type=int,
                        help='edit a note')
    parser.add_argument('-r', '--registry', action='store_true',
                        help='show the registry of all notes')
    parser.add_argument('-i', '--index', action='store_true',
                        help='show an index of clustered notes')
    parser.add_argument('-c', '--collect', type=int,
                        help='collect associated notes')
    parser.add_argument('-f', '--find', help='search for a specific word')
    parser.add_argument('-t', '--train-of-thought', type=int,
                        help='collect associated notes')
    parser.add_argument('--map', action='store_true',
                        help='map of notes in graphviz dot format')
    parser.add_argument('--inbox', action='store_true',
                        help='inbox containing unreferenced notes')
    # Parse options
    return parser.parse_args()


def output_note(output):
    """Open the default editor and send output over stdin.

    :output: text to send to the editor over stdin

    """
    editor = environ['EDITOR'] if 'EDITOR' in environ else 'vim'
    return run([editor, '-c', 'set ft=markdown', '-'], input=output, text=True)


def train_of_thought(v, zettelkasten, distance=None, output=None):
    """Display the train of though for a Note.

    :v: id of Note to start from
    :zettelkasten: zettelkasten instance to query
    :output: True if output must be sent to the default editor
    :returns: TODO

    """
    out = ''
    for h, note in zettelkasten.train_of_thought(v):
        if distance is not None and h >= distance:
            log.debug('{i:>5}. SKIPPED'.format(i=note.get_id()))
            continue
        log.info('{i:>5}. {t} [{h}]'.format(i=note.get_id(), t=note, h=h))
        out += note.get_body() + '\n'
    if output:
        output_note(out)


def map_notes(zettelkasten, output=None):
    """ """
    if output is None:
        raise ValueError('Output must be set (--output)')
    # Create the graph and write to [output]
    g = zettelkasten.get_graph()
    output_note(g.export_dot())


def collect_note(v, zettelkasten, output=None):
    """TODO: Docstring for collect_note.

    :v: TODO
    :zettekasten: TODO
    :returns: TODO

    """
    out = ''
    for note in zettelkasten.collect(v):
        log.info('{i:>5}. {t}'.format(i=note.get_id(), t=note))
        out += note.get_body() + '\n'
    if output:
        output_note(out)


def edit_note(note, zettelkasten):
    """TODO: Docstring for edit_note.

    :zettelkasten: TODO
    :returns: TODO

    """
    if not zettelkasten.exists(note.get_id()):
        raise ValueError('No Note for ID: "{i}" found'.format(i=note.get_id()))
    log.info('Editing note "{i}"'.format(i=note.get_id()))
    # Start $EDITOR, if set
    editor = environ['EDITOR'] if 'EDITOR' in environ else 'vim'
    call([editor, note.get_filename()])


def create_note(zettelkasten):
    """TODO: Docstring for create_note.
    :returns: TODO

    """
    note = zettelkasten.get_next_note()
    # Write template to file
    now = datetime.utcnow().isoformat()
    with open(note.get_filename(), 'w') as f:
        f.write('---\ntitle: ""\ndate: "{t}"\n---\n'.format(t=now))
    log.info('Created new note "{f}"'.format(f=note.get_filename()))
    # Edit the Note
    edit_note(note, zettelkasten)


def registry(zettelkasten):
    """TODO: Docstring for register.
    :returns: TODO

    """
    for c, note in zettelkasten.registry():
        log.info('{i:>5}. {t} [{c}]'.format(i=note.get_id(), t=note, c=c))


def inbox(zettelkasten):
    """TODO: Docstring for inbox.

    :returns: TODO

    """
    # Get all notes without links (inbox)
    for c, note in zettelkasten.inbox():
        log.info('{v:>5}. {t} [{c}]'.format(v=note.get_id(), t=note, c=c))


def index(zettelkasten, output=None):
    """TODO: Docstring for index.

    :zettelkasten: TODO
    :returns: TODO

    """
    log.info('Collecting Notes')
    # Get all clusters of Notes
    out = '# Generated index\n'
    for i, c in enumerate(zettelkasten.index(), start=1):
        log.info('{s:-^80}'.format(s=' Cluster: {i:0>5} '.format(i=i)))
        out += '\n## Cluster: {i:0>5}\n\n'.format(i=i)
        for note in sorted(c, reverse=True):
            log.info('{v:>5}. {t}'.format(v=note.get_id(), t=note))
            f, t = zettelkasten.get_edges_count(note.get_id())
            out += '* [{ti}]({v}) [in:{t}, out:{f}]'.format(v=note.get_id(),
                                                            ti=note,
                                                            f=f,
                                                            t=t) + '\n'
    if output:
        output_note(out)


def find(s, zettelkasten):
    """ Find any Notes that match search term s. """
    for note in zettelkasten.find(s):
        log.info('{v:>5}. {t}'.format(v=note.get_id(), t=note))


def main():
    """ Main entry point """
    options = parse()
    try:
        # Setup logging
        logger(options)
        log.info('{s:-^80}'.format(s=" That's just like, your opinon, man "))

        zettelkasten = Zettelkasten(options.zettelkasten)

        # Do command line arguments
        if options.collect:
            collect_note(options.collect, zettelkasten, options.output)
        if options.create:
            create_note(zettelkasten)
        if options.edit:
            edit_note(zettelkasten.get_note(options.edit), zettelkasten)
        if options.registry:
            registry(zettelkasten)
        if options.index:
            index(zettelkasten, options.output)
        if options.find:
            find(options.find, zettelkasten)
        if options.train_of_thought:
            train_of_thought(options.train_of_thought, zettelkasten,
                             options.distance, options.output)
        if options.map:
            map_notes(zettelkasten, options.output)
        if options.inbox:
            inbox(zettelkasten)
    except KeyboardInterrupt:
        log.info('Received <ctrl-c>, stopping')
    except Exception as e:
        log.exception(e) if options.debug else log.error(e)
    finally:
        log.info('{s:-^80}'.format(s=" Fuck it dude. Let's go bowling "))
        return(0)


if __name__ == "__main__":
    exit(main())
