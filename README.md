# The Dude Abides

*The dude abides* is a small command line tool written in Python3 and helps
with managing a [Zettelkasten](https://zettelkasten.de/introduction/). Long
story short: create a new note using the dude, add cool stuff to the note and
link to other notes, using standard Markdown syntax. Once you've created some
notes, render to (static) HTML and upload to a webhost.

## Concept

The dude is heavily inspired (implements?) the [lattice of
thoughts](https://zettelkasten.de/posts/lattice-of-thoughts/). In this way of
thinking, notes that reference eachother form a lattice (sequence). All these
notes are related in a way that makes sense to the author of the Zettelkasten
(you read the introduction, right?). In the visualisation below, notes 6, 5, 4
and 9 form a *lattice of thought*.

![Lattice of thoughts](https://raw.githubusercontent.com/r1tger/the-dude-abides/master/doc/relations-20200919.svg)

This way of thinking is interesting, as a lattice implies both a *start*
(entry) and *end* (exit) note. Lattices can also merge and split. An example of
this is entry note 1, which can be reached from exit notes 8 and 14. Entry
notes are automatically detected (have no outgoing references, are only
referred to from other notes). If no notes match the criteria for an entry note
or if a circular reference (1 refers to 2, 2 refers to 3 and 3 refers back to
1) was created, notes can be manually marked as an entry note.

## What makes the dude unique?

*The dude* incorporates the concept of *entry* and *exit* notes and works to
improve on this:

1. when rendered, the Zettelkasten includes a list of all entry notes, which
   are a starting point for each *lattice*. This of an entry note as the first
   note of something you are interested in;
2. every following note in the lattice refers to the previous note, until a
   note is found which refers to another note, but is never referenced itself.
   This is an exit note;
3. each rendered note includes a list of referring notes (notes that link to
   the rendered note) as a reference. This list of references does not only
   include direct references (notes that have a Markdown link to the referred
   note), but also any exit notes that can be reached from the rendered note.

Point 3 is the big one. Not only is the reference to the exit note detected and
added to the rendered note, the entire lattice from rendered note to exit note
can be opened with one click. This answers the question: "**how** is the
rendered note connected to the exit note?"

If you're reading this and you're a bit familiar with graph theory, you know
that an extremely large number of lattices may be found from any given note to
any given exit note, as the number of notes in the Zettelkasten grows. This
makes working with all possible lattices extremely impractical and risks losing
overview of the Zettelkasten, sidestepping our goals for the Zettelkasten (I'm
serious, go read the introduction!).

A solution is needed. One of the quantifiable things that make a note valuable
is the number of times a note is referred to. Notes that are linked to from
other notes become *hubs* for related notes: any referring note can be found by
looking at the hub note. The dude takes the number of times two connected notes
are referred to and adds this information as a property (weight) of the
connection between those two notes. Using this information, the shortest path
between a note and exit note is determined, resulting in the fewest number of
most "valuable" notes to make a sensible lattice of thought. This also limits
the number of possible lattices added to a rendered note, keeping everything
neat and tidy.

Of course, all the other connections remain valid and valuable as well, which
is why *the dude* provides functionality to extract all notes by ID, until
either all entry or exit notes are reached. This creates an outline of all
connected notes relevant to the note that was selected, which can then be
expanded into an article, presentation, blog post, or even book.

# Installing

To get up and running, install directly from Github into your home directory:

```bash
$ pip3 install --user git+https://github.com/r1tger/the-dude-abides
$ thedudeabides --help
```

# Using

```bash
$ thedudeabides --help
Usage: thedudeabides [OPTIONS] COMMAND [ARGS]...

  That's just like, your opinon, man.

Options:
  --zettelkasten PATH  Directory containing the zettelkasten.
  --debug              Enable debug mode.
  --help               Show this message and exit.

Commands:
  create        Create a new note, providing the title.
  edit          Edit a note by ID.
  index         Show an index of clustered notes.
  predecessors  Collect train of thought by ID.
  render        Render all notes as HTML.
  successors    Collect associated notes by ID.
```

## Creating notes

The dude will work on the current directory if no --zettelkasten parameter is
provided, so create a separate directory and create a new (first) note:

```bash
$ mkdir Zettelkasten/ && cd Zettelkasten/
$ thedudeabides create 'My first note'
```

Once created, the note is opened in the default $EDITOR. Edit as required and
save. Notes are written using standard Markdown syntax and can include links,
tables formattting and everything else that works from Markdown. Each note has
a unique identifier (starting at 1), based on the number of existing notes in
the Zettelkasten directory.

Now create a second note an add a Markdown link to the first one note in the
text:

```bash
[My first note](1) is a good note that I'm referencing here.
```

Finding notes based on (fuzzy) text search is something that should be done
from your editor, as everything is plain text Markdown, any editor supporting
searching on file contents works fine.

## Rendering to HTML

*The dude* can render all notes in the Zettelkasten as HTML files to simplify
navigating the Zettelkasten (and see all lattices!). Create separate directory
from HTML output and render:

```bash
$ mkdir HTML/
$ thedudeabides render HTML/
$ cd HTML/ && python3 -m SimpleHTTPServer 8080
```

The last line is optional, but allows you to navigate to
`http://localhost:8080` using your browser and browse the rendered
Zettelkasten. To complete the rendered pages, copy the contents of the `data/`
directory from the thedudeabides distribution to the `HTML/` directory.

Additionaly, the entire `HTML/` directory can be uploaded to a webhost to make
the Zettelkasten available across the internet.

# Developing

If you'd like to contribute to development of the dude, set up a development
environment:

```bash
$ git clone https://github.com/r1tger/the-dude-abides
$ cd the-dude-abides
$ python3 -m venv env
$ source env/bin/activate
$ pip install --editable .
```

Now edit any files in the ```thedudeabides/``` package and submit a pull
request.

# TO-DO

* add *more* documentation;
* add other types of Zettelkasten software.
