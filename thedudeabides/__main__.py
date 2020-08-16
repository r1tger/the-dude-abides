#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .zettelkasten import Zettelkasten

from argparse import ArgumentParser
from os import environ
from os.path import expanduser, join, isdir
# from pprint import pprint
from subprocess import call, run
from sys import exit
from jinja2 import Environment
from datetime import datetime

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
    # Note specific
    parser.add_argument('--create', default='',
                        help='create a new note, providing the title')
    parser.add_argument('-e', '--edit', type=int,
                        help='edit a note by ID')
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
    parser.add_argument('--render', help='Render all notes as HTML')
    # Parse options
    return parser.parse_args()


def output_note(output):
    """Open the default editor and send output over stdin.

    :output: text to send to the editor over stdin

    """
    editor = environ['EDITOR'] if 'EDITOR' in environ else 'vim'
    return run([editor, '-c', 'set ft=markdown', '-'], input=output, text=True)


def train_of_thought(v, zettelkasten):
    """Display the train of though for a Note.

    :v: id of Note to start from
    :zettelkasten: zettelkasten instance to query
    :returns: TODO

    """
    log.info('Collecting Notes')
    output_note(zettelkasten.train_of_thought(v).get_contents())


def map_notes(zettelkasten):
    """ """
    # Create the graph and write to [output]
    output_note(zettelkasten.get_graph().export_dot())


def render_notes(zettelkasten, output):
    """TODO: Docstring for render_notes.

    :zettelkasten: TODO
    :output: TODO
    :returns: TODO

    """
    log.info('Rendering notes')
    if not isdir(output):
        raise ValueError('Invalid output directory provided')

    for note in zettelkasten.render():
        # Write to disk
        filename = join(output, '{v}.html'.format(v=note.get_id()))
        with open(filename, 'w') as f:
            f.write(note.render())
    # Write the index to disk
    with open(join(output, 'index.html'), 'w') as f:
        f.write(zettelkasten.index().render())


def collect_note(v, zettelkasten):
    """TODO: Docstring for collect_note.

    :v: TODO
    :zettelkasten: TODO
    :returns: TODO

    """
    log.info('Collecting Notes')
    output_note(zettelkasten.collect(v).get_contents())


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


def create_note(zettelkasten, title):
    """TODO: Docstring for create_note.
    :returns: TODO

    """
    note = zettelkasten.create_note(title)
    # Write template to file
    with open(note.get_filename(), 'w') as f:
        f.write(note.get_contents())
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


def index(zettelkasten):
    """TODO: Docstring for index.

    :zettelkasten: TODO
    :returns: TODO

    """
    log.info('Collecting Notes')
    output_note(zettelkasten.index().get_contents())


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

        zettelkasten = Zettelkasten(expanduser(options.zettelkasten))

        # Do command line arguments
        if options.collect:
            collect_note(options.collect, zettelkasten)
        if options.create:
            create_note(zettelkasten, options.create)
        if options.edit:
            edit_note(zettelkasten.get_note(options.edit), zettelkasten)
        if options.registry:
            registry(zettelkasten)
        if options.index:
            index(zettelkasten)
        if options.find:
            find(options.find, zettelkasten)
        if options.train_of_thought:
            train_of_thought(options.train_of_thought, zettelkasten)
        if options.render:
            render_notes(zettelkasten, expanduser(options.render))
        if options.map:
            map_notes(zettelkasten)
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
