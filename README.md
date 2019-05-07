
# enex-org

The aim of this project is to convert the ENML contents of an Evernote export file (.enex) into emacs org-mode file (.org), with corresponding syntax, where applicable.

Written in Python. It also requires [the lxml library](http://lxml.de/) to run.

Written partly for study, partly to try toconvert some notes I saved in evernote. Much is based on enex2org (https://github.com/jkarres/enex2org), which I found googling for solutions. 


## How to run enex-org:

``` shell
python enexorg.py mynotes.enex
```

Running the above command should create file `mynotes.org` under folder `mynotes`. If the folder and file already exists, it will overwrite them.

I have noticed that, in certain conditions, trying to run enexorg.py to overwrite an existing file will throw an error. It seems to succeed the second time around.

## Current State:

### What enexorg can currently do:

  * It seems able to *very crudely* convert .enex files containing relatively simple text notes. 
  * It can convert italicized, bold, and underlined texts, as well as links.

### Some of the things it cannot (yet) do:

  * Headers within note content (h1, h2, ...) are not converted.
  * Properly indent note contents, such as nested lists.
  * Tables are not implemented/checked. (The unchecked part of the code (enstring.py) I copied from may partially render them.)
  * Resources, such as images, attached files like PDF, are ignored.
  * I'm not sure what happens to links containing other Evernote notes.
  * Tags are ignored. (Since there can be many tags on a note, I'm debating whether these should be converted to org-mode tags, or placed in the :PROPERTY: drawer.
