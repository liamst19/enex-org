#!/usr/bin/env python
# -*- coding: utf-8 -*-

# en2string.py

# Based on enml.py from enex2org (https://github.com/jkarres/enex2org).
# Rips the HTML content from a <en-note> element, converting
# HTML tags into corresponding org-mode syntax. Returns as string.


import os
from lxml import etree as ET
import uuid
import datetime
import re
from contextlib import contextmanager

#### ContextManager ####

INDENT = object()
DEDENT = object()
START_ROW = object()
END_ROW = object()
LIST_ITEM = object()
BEGIN_ORDERED = object()
END_ORDERED = object()
BEGIN_UNORDERED = object()
END_UNORDERED = object()

# RegEx patterns
LINK_RE = re.compile(r'\[\[(.*?)\]\[(.*)\]\]$')
BRACKET_RE = re.compile(r'\[\[[^\[\]]*?\]\[[^\[\]]*?\]\]| +|\n|[^ \n]+')

SPC_OPN_RE = re.compile('^([ ,]*)')
SPC_CLS_RE = re.compile('([ ,]*)$')
COMMA_OPN_RE = re.compile(r'^\,')
COMMA_CLS_RE = re.compile(r'\,$')

SPAN_DEC_RE = re.compile(r'(italic|bold|underline)?')
DEC_RE = re.compile(r'i|b|u|span')

# --------------------------

def get_spc(elt):
    """Returns leading and trailing spaces, if there are any"""
    t = elt.text
    s_opn = ''
    s_cls = ''

    if t:
        s_opn = SPC_OPN_RE.search(t).group(0)
        s_cls = SPC_CLS_RE.search(t).group(0)

    return s_opn, s_cls

@contextmanager
def span(rv, elt, note):
    s_opn, s_cls = get_spc(elt)
    span_attrib = elt.attrib.get('style')
    decor = ''
    s = ''
    
    if span_attrib:
        decor = SPAN_DEC_RE.search(span_attrib).group(0)

    if decor == 'italic':
        s = '/'
    elif decor == 'bold':
        s = '*'
    elif decor == 'underline':
        s = '_'
    
    rv.append(s_opn)    
    rv.append(s)
    yield
    rv.append(s)
    rv.append(s_cls)

# --------------------------

@contextmanager
def italics(rv, elt, note):
    s_opn, s_cls = get_spc(elt)
    dec = '/'

    rv.append(s_opn)
    rv.append(dec)
    yield
    rv.append(dec)
    rv.append(s_cls)
    
@contextmanager
def underline(rv, elt, note):
    s_opn, s_cls = get_spc(elt)
    dec = '_'

    rv.append(s_opn)
    rv.append(dec)
    yield
    rv.append(dec)
    rv.append(s_cls)

@contextmanager
def bold(rv, elt, note):
    s_opn, s_cls = get_spc(elt)
    dec = '*'

    rv.append(s_opn)
    rv.append(dec)
    yield
    rv.append(dec)
    rv.append(s_cls)

@contextmanager
def link(rv, elt, note):
    # we want to keep this as a single chunk for word-wrap purposes
    # forgive me...
    old_len = len(rv)
    yield
    assert(all(isinstance(x, str) for x in rv[old_len:]))
    description = ''.join(rv[old_len:])
    del rv[old_len:]
    rv.append('[[{}][{}]]'.format(elt.attrib.get('href', '') or '', description))

# --------------------------    

@contextmanager
def add_newline(rv, elt, note):
    if rv and type(rv[-1]) is str and rv[-1] and rv[-1][-1] != '\n':
        rv.append('\n')
    yield
    rv.append('\n')
    
@contextmanager
def br(rv, elt, note):
    rv.append('\n')
    yield

@contextmanager
def horizontal_rule(rv, elt, note):
    rv.append('\n----------\n')
    yield
    
# --------------------------
# Table 
# --------------------------

@contextmanager
def table(rv, elt, note):
    rv.append('\n|-')
    yield
    rv.append('\n|-')
    
@contextmanager
def table_row(rv, elt, note):
    rv.append('\n')
    rv.append(START_ROW)
    yield
    rv.append(END_ROW)

@contextmanager
def table_cell(rv, elt, note):
    rv.append('| ')
    yield

# --------------------------
# Lists
# --------------------------

@contextmanager
def unordered_list(rv, elt, note):
    rv.append(BEGIN_UNORDERED)
    yield
    rv.append(END_UNORDERED)

@contextmanager
def ordered_list(rv, elt, note):
    rv.append(BEGIN_ORDERED)
    yield
    rv.append(END_ORDERED)

@contextmanager
def list_item(rv, elt, note):
    rv.append(LIST_ITEM)
    rv.append(INDENT)
    yield
    rv.append(DEDENT)

# --------------------------

@contextmanager
def todo(rv, elt, note):
    rv.append('[ ] ')
    yield

@contextmanager
def media(rv, elt, note):
    filename = 'RESOURCE_FILENAME' #note.resources[elt.attrib['hash']].filename
    attachment_dir = 'NOTE_ATTACHMENT_DIR' #note.attachment_dir
    rv.append('[[file:{}][{}]]'.format(
        os.path.join(attachment_dir, filename),
        filename))
    yield

@contextmanager
def default(rv, elt, note):
    yield

################################################
    
tag2contextmgr = {
    'span': span,
    'i': italics,
    'li': list_item,
    'en-todo': todo,
    'strong': bold,
    'a': link,
    'u': underline,
    'b': bold,
    'tr': table_row,
    'td': table_cell,
    'th': table_cell,
    'table': table,
    'div': add_newline,
    'hr': horizontal_rule,
    'ul': unordered_list,
    'ol': ordered_list,
    'br': br,
    'en-media': media,
}

################################################

def convert_note(note):
    """Convert the content of a Note object into a string."""

    def process_elt(elt, rv):
        """Analyze XML element elt and fills array rv"""
        
        with tag2contextmgr.get(elt.tag, default)(rv, elt, note):
            txt = elt.text
            if txt:
                
                # ** TODO: Seems rather inelegant, look for other solutions **
                # Strip leading and trailing spaces and commas if <i>,<b>,
                # <u>,<span>. The spaces are replaced in @contextmanager functions
                if DEC_RE.match(elt.tag):
                    txt = txt.strip()
                    txt = COMMA_OPN_RE.sub('', txt)                    
                    txt = COMMA_CLS_RE.sub('', txt)
                #--------------------------------------------------
                
                txt = txt.replace('\n', '')
                rv.append(txt)
            for c in elt:
                if elt.tag == 'div' and c.tag == 'br':
                    # you'll get stuff like <div><br/></div> where you'll only
                    # want a single newline
                    pass
                else:
                    process_elt(c, rv)
                if c.tail:
                    rv.append(c.tail.replace('\n', ''))

    indent_level = 0 # for keeping track of nested lists
    in_row = False # are we currently in a table row?
    new_strs = [] # we're going to cat these together as our final answer
    lists = [] # used as a stack to track nested sublists
               # an int represents the position in an ordered list
               # a None represents an unordered list
    rv = [] # gets passed through the process_elt function
    column = 0
    
    process_elt(note, rv) #fill rv

    # Iterate through filled array
    for item in rv:

        # insert appropriate indentation and newlines
        if item is None:
            continue
        if item is INDENT:
            indent_level += 1
        if item is DEDENT:
            indent_level -= 1
        if item is START_ROW:
            in_row = True
        if item is END_ROW:
            in_row = False
        if item is BEGIN_ORDERED:
            lists.append(1)
        if item is END_ORDERED:
            lists.pop()
        if item is BEGIN_UNORDERED:
            lists.append(None)
        if item is END_UNORDERED:
            lists.pop()
        if item is LIST_ITEM:
            item = '\n- '
            # if lists[-1]: # are we in an ordered list?
            #     item = '\n' + str(lists[-1]) + '. '
            #     lists[-1] += 1
            # else:
            #     item = '\n- '
        
        if isinstance(item, str):
            if in_row:
                new_strs.append(item.replace('\n', ''))
            else:
                
                # link or spaces or newline or other
                for chunk in BRACKET_RE.findall(item):
                    # len as displayed in org mode
                    mo = LINK_RE.search(chunk)
                    if mo is not None:
                        chunk_len = len(mo.group(2))
                    else:
                        chunk_len = len(chunk)

                    if chunk == '\n':
                        new_strs.append('\n' + '  '*indent_level)
                        column = 2 * indent_level
                    elif column + chunk_len < 80:
                        new_strs.append(chunk)
                        column += chunk_len
                    else:
                        if chunk[0] == ' ':
                            pass
                        else:
                            ## delete trailing whitespace
                            # if new_strs and new_strs[-1][0] == ' ':
                            #    del new_strs[-1]
                            # new_strs.append('\n' + '  '*indent_level + chunk)
                            new_strs.append(chunk)
                            column = 2 * indent_level + chunk_len

    return ''.join(new_strs)

################################################

def enml2xhtml(root, resd):
    """Convert the given ET.Element into html.  Return that html along with
    a set containing the hashes of the resources that were incorporated
    into that html (so we don't bother writing them out as attachments
    unnecessarily).

    root -- the ET.Element
    resd -- the hash->resource dict
    """
    used_resource_hashes = set()
    for elt in root.iter():
        if elt.tag == 'en-note':
            elt.tag = 'body'
        elif elt.tag == 'en-media':
            used_resource_hashes.add(elt.attrib['hash'])
            mime_type = elt.attrib.get('type', '/')
            data_str = 'data:{};base64,{}'.format(
                mime_type,
                resd[elt.attrib['hash']].base64data)
            if mime_type.split('/')[0] == 'image':
                elt.tag = 'img'
                elt.attrib['src'] = data_str
            else:
                elt.tag = 'a'
                elt.attrib['href'] = data_str
                elt.text = resd[elt.attrib['hash']].filename
        elif elt.tag == 'en-crypt':
            elt.tag = 'div'
        elif elt.tag == 'en-todo':
            elt.tag = 'div'
    return used_resource_hashes, ET.tostring(root)
