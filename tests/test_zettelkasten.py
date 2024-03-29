# -*- coding: utf-8 -*-

from thedudeabides.note import Note

import pytest
from datetime import date


NOTE_01 = """---
title: "Purus vitae"
date: "2020-08-09T00:00:00.000000"
---

Aenean vel purus vitae felis consectetur hendrerit at in enim. Quisque et purus
libero. Vestibulum in [ipsum](3) nisi. Maecenas condimentum leo congue ornare
dictum. Quisque ac facilisis nunc. Fusce [quis](3) lobortis nisi. Sed iaculis
nec sem non tincidunt. Nullam sodales nunc a pellentesque accumsan.
"""

NOTE_02 = """---
title: "Ante vel ipsum"
date: "2020-08-09T00:00:00.000000"
---

In pulvinar varius ante. Nulla at lobortis tellus. Donec vulputate ex auctor
imperdiet elementum. Sed blandit ante vel ipsum facilisis, sed laoreet elit
malesuada.

$\alpha = \frac{1}{2}$

Nam a interdum lectus. Pellentesque semper nisi ac ante interdum
pellentesque. Nulla a felis in arcu lobortis viverra aliquam eu odio.
"""

NOTE_03 = """---
title: "feugiat magna blandit"
date: "2020-08-09T00:00:00.000000"
---

Morbi placerat gravida tortor lacinia euismod. [Suspendisse](1) ut feugiat
turpis.  Ut pretium ultrices commodo. Etiam [mollis](1) sapien magna, in
blandit diam condimentum id. Suspendisse sodales feugiat nibh [ac](3)
dignissim.
"""


@pytest.fixture
def zettelkasten(tmpdir):
    """ """
    from thedudeabides.zettelkasten import Zettelkasten
    directory = tmpdir.mkdir('zk')
    # Add test notes
    open(directory.join('1.md'), 'w').write(NOTE_01)
    open(directory.join('2.md'), 'w').write(NOTE_02)
    open(directory.join('3.md'), 'w').write(NOTE_03)
    return Zettelkasten(directory)


def test_successors(zettelkasten):
    """ """
    zettelkasten.successors(1)


def test_create_note(zettelkasten):
    """ """
    note = zettelkasten.create_note('Test note')
    assert(isinstance(note, Note))
    assert(note.get_id() == 4)


def test_exists(zettelkasten):
    """ """
    assert(zettelkasten.exists(1))
    assert(zettelkasten.exists(2))
    assert(zettelkasten.exists(3))
    assert(not zettelkasten.exists(99))


def test_index(zettelkasten):
    """ """
    zettelkasten.index()


def test_predecessors(zettelkasten):
    """ """
    zettelkasten.predecessors(3)


def test_render(zettelkasten):
    """ """
    zettelkasten.render()


def test_register(zettelkasten):
    """ """
    zettelkasten.register()


def test_lint(zettelkasten):
    zettelkasten.lint()


def test_lattice(zettelkasten):
    zettelkasten.lattice(2)


def test_today(zettelkasten):
    zettelkasten.today(date.fromisoformat('1983-05-14'))
