#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .zettelkasten import Zettelkasten

from click import (option, Path, pass_context, group, argument,
                   make_pass_decorator, progressbar, INT, BOOL)
from os import environ
from os.path import join
# from pprint import pprint
from subprocess import run
from sys import exit
from datetime import date

import logging
log = logging.getLogger(__name__)

LOG_FORMAT = '[%(levelname)s] [%(relativeCreated)d] %(message)s'
EDITOR = 'vim'

# Make the Zettelkasten instance available as a decorator for click
pass_zk = make_pass_decorator(Zettelkasten)


def edit_note(note, output='-'):
    """Open the default editor and send output over stdin.

    :note: Note to send to the editor.
    :output: filename of file to edit, or stdin as default.

    """
    editor = environ['EDITOR'] if 'EDITOR' in environ else EDITOR
    input = note.get_contents() if output == '-' else None
    return run([editor, '-c', 'set ft=markdown', output], input=input,
               text=True)


@group()
@option('--zettelkasten', type=Path(exists=True, dir_okay=True,
        resolve_path=True), help='Directory containing the zettelkasten.',
        default='.')
@option('--debug', is_flag=True, default=False, help='Enable debug mode.')
@pass_context
def main(ctx, zettelkasten, debug):
    """That's just like, your opinon, man.
    """
    # Setup logging
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    # Add handler to the root log
    logging.root.addHandler(handler)
    # Set log level
    level = logging.DEBUG if debug else logging.INFO
    logging.root.setLevel(level)
    # Allow the Zettelkasten instance to be passed between functions
    ctx.obj = Zettelkasten(zettelkasten)


@main.command()
@argument('v', type=INT)
@option('--depth', type=INT, default=99)
@pass_zk
def predecessors(zk, v, depth):
    """Collect train of thought by ID.
    """
    try:
        log.info('Collecting note "{v}"'.format(v=v))
        edit_note(zk.predecessors(v, depth))
    except ValueError as e:
        log.error(e)


@main.command()
@argument('v', type=INT)
@option('--depth', type=INT, default=99)
@pass_zk
def successors(zk, v, depth):
    """Collect associated notes by ID.

    The provided ID is treated as the endpoint with all notes retrieved up
    until all starting points.
    """
    try:
        log.info('Collecting note "{v}"'.format(v=v))
        edit_note(zk.successors(v, depth))
    except ValueError as e:
        log.error(e)


@main.command()
@argument('title')
@pass_zk
def create(zk, title):
    """Create a new note, providing the title.
    """
    note = zk.create_note(title)
    # Write template to file
    with open(note.get_filename(), 'w') as f:
        f.write(note.get_contents())
    log.info('Created new note "{f}"'.format(f=note.get_filename()))
    # Edit the Note
    edit_note(note, note.get_filename())


@main.command()
@argument('v', type=INT)
@pass_zk
def edit(zk, v):
    """Edit a note by ID.
    """
    log.info('Editing note "{v}"'.format(v=v))
    # Get Note to edit
    note = zk.get_note(v)
    edit_note(note, note.get_filename())


@main.command()
@pass_zk
def index(zk):
    """Show an index of clustered notes.
    """
    log.info('Collecting Notes')
    edit_note(zk.index())


@main.command()
@argument('output', type=Path(exists=True, dir_okay=True, resolve_path=True))
# @argument('norandom', default=False, type=INT)
@option('--no-random', is_flag=True, default=False,
        help='Disable generation of random lattices.')
@option('--days', default=3, type=INT,
        help='Number of days in the past to look for notes.')
@pass_zk
def render(zk, output, no_random, days):
    """Render all notes as HTML.
    """
    log.info('Rendering notes to "{d}"'.format(d=output))
    with progressbar(zk.render(no_random), length=zk.count(),
                     label='Rendering notes') as bar:
        for note in bar:
            # Write to disk
            filename = join(output, '{v}.html'.format(v=note.get_id()))
            with open(filename, 'w') as f:
                f.write(note.to_html())
    # Write the index to disk
    with open(join(output, 'index.html'), 'w') as f:
        f.write(zk.index().to_html())
    # Write the register to disk
    with open(join(output, 'register.html'), 'w') as f:
        f.write(zk.register(days).to_html())
    # Write the tags to disk
    with open(join(output, 'tags.html'), 'w') as f:
        f.write(zk.tags().to_html())
    # Write the search page to disk
    with open(join(output, 'search.html'), 'w') as f:
        f.write(zk.inverted_index())
    log.info('Completed rendering of notes')


@main.command()
@argument('birthday', default='1983-05-14')
@option('--days', default=3, type=INT,
        help='Number of days in the past to look for notes.')
@pass_zk
def today(zk, birthday, days):
    """Show some statistics for today.
    """
    log.info('Starting the day ...')
    edit_note(zk.today(date.fromisoformat(birthday), days))


@main.command()
@pass_zk
def lint(zk):
    """
    """
    log.info('Finding reciprocal relations ...')
    zk.lint()


@main.command()
@argument('v', type=INT)
@pass_zk
def lattice(zk, v):
    """
    """
    edit_note(zk.lattice(v))


if __name__ == "__main__":
    exit(main())
