#!/usr/bin/env python
# -*- coding: utf-8 -*-

# enex-org

import sys
import os
import shutil
import re
import argparse
from lxml import etree as ET
import base64
import hashlib
from collections import namedtuple, defaultdict

import ennote # ennote.py contains Note class

def iter_notes(enexpath):
    """Iterates through elements of the XML file 
    at enexpath, yield note elements."""

    # when title contains &nbsp; this throws an error.
    for event, elem in ET.iterparse(enexpath, tag='note', html=True):
        if elem.tag == 'note':
            yield ennote.Note(elem)
            elem.clear() #release memory

            
def output_headers(outfile, title):
    """Writes file headers to outfile"""
    outfile.write('#+TITLE: ' + title)
    outfile.write(ennote.newline())
    outfile.write('#+STARTUP: content')
    outfile.write(ennote.newline(2))    
    
        
def output_entry(outfile, org_entry):
    """Outputs the note element into target orgpath"""
    outfile.write(org_entry)
    outfile.write(ennote.newline())
    

def prepare_dir(enexpath, notebook):
    """Prepares directory for output"""

    # Prepare file name and path
    orgfile =  notebook + '.org'
    orgpath = os.path.join(notebook, orgfile)

    # Check if path exists
    if os.path.exists(notebook):
        # Delete Folder and its contents -- later change to Prompt for action
        shutil.rmtree(notebook)

    # Create directory
    os.makedirs(notebook)
    
    return orgpath


########
# Main #
########
    
def convert_enex_to_org(enexpath):
    """Converts .enex file to .org file"""

    # Prepare output directory
    notebook = re.search("(.+).enex$", enexpath).group(1)
    orgpath = prepare_dir(enexpath, notebook)
    
    # open output file
    notecount = 0
    with open(orgpath, encoding='utf-8', mode='w') as outfile:
              # Add file headers
              output_headers(outfile, notebook)

              # While output file is open, iterate through enex XML for notes
              for note in iter_notes(enexpath):
                  # convert and write to output
                  output_entry(outfile, note.get_org_entry())
                  notecount += 1


    print('{} entries in {} created.'.format(str(notecount), orgpath))

########
if __name__ == '__main__':
    
   
    # Define arguments
    argparser = argparse.ArgumentParser(
        description='Converts Evernote export file (.enex) to org-mode (.org)')
    argparser.add_argument('input', help='path to .enex file') 
    # argparser.add_argument('output', help='path of target .org file')

    # Get the arguments
    args = argparser.parse_args()
    # if os.path.exists(args.output):
    #     # Exit if output file already exists
    #     print('{} already exists.'.format(args.output))
    #     sys.exit(1)

        # Alternately, prompt if user wants to overwrite

    # Begin conversion
    convert_enex_to_org(args.input)

#########
