#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .zettelkasten import Zettelkasten

from click import (option, Path, pass_context, group, argument,
                   make_pass_decorator, INT)
from os import environ
from os.path import join
# from pprint import pprint
from subprocess import run
from sys import exit

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
@argument('s', type=INT)
@argument('t', type=INT)
@pass_zk
def choo_choo(zk, s, t):
    """Collect train of thought by ID.
    """
    try:
        log.info('Collecting train of thought "{s}" to "{t}"'.format(s=s, t=t))
        edit_note(zk.train_of_thought(s, t))
    except ValueError as e:
        log.error(e)


@main.command()
@argument('v', type=INT, nargs=-1)
@pass_zk
def collect(zk, v):
    """Collect associated notes by ID.

    The provided ID is treated as the endpoint with all notes retrieved up
    until all starting points.
    """
    try:
        log.info('Collecting Notes "{v}"'.format(v=', '.join(map(str, v))))
        edit_note(zk.collect(v))
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
@pass_zk
def render(zk, output):
    """Render all notes as HTML.
    """
    log.info('Rendering notes to "{d}"'.format(d=output))
    for note in zk.render():
        # Write to disk
        filename = join(output, '{v}.html'.format(v=note.get_id()))
        with open(filename, 'w') as f:
            f.write(note.render())
    # Write the index to disk
    with open(join(output, 'index.html'), 'w') as f:
        f.write(zk.index().render())
    # Write the register to disk
    with open(join(output, 'register.html'), 'w') as f:
        f.write(zk.register().render())
    log.info('Completed rendering of notes')


if __name__ == "__main__":
    exit(main())
