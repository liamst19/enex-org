#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ennote.py

# Details of the Evernote export file (.enex) format is given
# in the following web article:
# https://blog.evernote.com/tech/2013/08/08/evernote-export-format-enex/

import os
from lxml import etree as ET
import uuid
import datetime
import re

### 
import enstring


class Note:
    def __init__(self, note_element):
        """Initialize the class instance"""
                
        # In the case the output will render multiple notebooks
        self.level = 1
 
        # header and main contents
        self.title = clean_text(note_element.find('title').text)
        self.content = enstring.convert_note(note_element.find('content').find('en-note'))

        # this date will be entered at the end of the note_element
        self.created = note_element.find('created').text

        # the following will be rendered under :PROPERTIES: drawer
        self.tags = [e.text for e in note_element.findall('tag')]
        self.sourceurl = note_element.find('note-attributes/source-url')

        # Do something with Resources
        
        # are the following necessary?
        self.uuid = str(uuid.uuid4())
        self.attachment_dir = os.path.join('data', self.uuid[:2], self.uuid[2:])        
        
    def get_org_entry(self):
        """Render note element into org entry"""

        title = self.get_org_bullets() + ' ' + self.get_org_title()
        tags = self.get_org_tags()
        properties = self.get_org_properties()
        body = self.get_org_content()
        date = self.get_org_created()

        orgentry = title + newline()
        orgentry += properties + newline(2)
        orgentry += body + newline(2)
        orgentry += date + newline()

        return orgentry

    
    def get_org_title(self):
        """Render title as org-mode header"""
        titletxt = self.title
        if titletxt == '':
            titletext = 'UNTITLED NOTE'
        return titletxt

    
    def get_org_bullets(self):
        """Render header bullets"""

        lvl = self.level

        if lvl < 1:
            lvl = 1
        
        startxt = '*' * lvl
        return startxt
    
    
    def get_org_tags(self):
        """Render org-mode tags"""
        tagtxt =''
        return tagtxt

    
    def get_org_content(self):
        """Render content body as org-mode entry text."""
        bodytxt = clean_text(self.content)
        return  bodytxt

        
    def get_org_properties(self):
        """Render miscellaneous properties"""
        propertytxt = '  :PROPERTIES:'
        propertytxt += newline()
        # write properties

        # close properties drawer
        propertytxt += '  :END:'
        
        return propertytxt


    def get_org_created(self):
        """Get date created"""
        datetxt = format_date(self.created)
        return datetxt


    def read_resources(self):
        """Initialize resources"""

        
    def format_resources(self):
        """Save resources into a resources directory"""


# Helper Functions

def format_date(date):
    """formats the date to org-mode timestamp"""
    
    sdate = datetime.datetime.strptime(date[0:13], '%Y%m%dT%H%M')
    datetxt = '[' + sdate.strftime('%Y-%m-%d %a %H:%M') + ']'
    return datetxt
            
def clean_text(txt):
    """Clean up and encode text to utf-8"""
    txt = re.sub('&nbsp;|\u00A0', ' ', txt)
    txt = re.sub('\n\* ', '\n\\* ', txt)
    return txt

def newline(lines=1):
    """Get linebreaks"""
    return '\n' * lines

    
