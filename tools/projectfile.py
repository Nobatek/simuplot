#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Use this script to create or delete the project file
# Usage: 
# ./project_file.py --create
# ./project_file.py --delete

import os
from os.path import join, dirname, abspath
import sys
import argparse
import fnmatch

# Project name (this is the name of the .pro file)
project = 'simuplot'

# List or languages
# ts files for these languages will be generated/updated
languages = ['fr',]

class ProjectFileManager(object):

    def __init__(self):

        # Application absolute base path
        self._base_path = join(dirname(dirname(abspath(__file__))), 'src')

        # Project file path
        self._project_file_path = join(self._base_path, 'simuplot.pro')

    @property
    def file_path(self):
        return self._project_file_path
    
    def create(self):

        # Relatives paths inside application
        simuplot_relpath = 'simuplot'
        ui_files_relpath = 'resources/ui'
        ts_files_relpath = 'i18n/ts'

        try:
            pf = open(self._project_file_path, "wb")
        except IOError:
            raise IOError("Can't open project file.")

        # Source files and ui files are stored in different directories
        # with the same directory structure
        subdirs = ['', 'datareader/', 'dataplotter/']

        def add_files(categ, rel_base, ext):
            """Find all files with extension ext in rel_base subdirs
               and print file relative paths in corresponding category 
               in project path
            """

            pf.write(categ +' = ')

            for sdir in subdirs:
                for f in os.listdir(join(self._base_path, rel_base, sdir)):
                    for e in ext:
                        if fnmatch.fnmatch(f, '*.' + e):
                            pf.write(join(rel_base, sdir, f) + ' ')
            
            pf.write('\n')

        # FORMS
        add_files('FORMS', ui_files_relpath, ['ui',])

        # SOURCES
        add_files('SOURCES', simuplot_relpath, ['py',])

        # TRANSLATIONS
        pf.write('TRANSLATIONS = ')
        for l in languages:
            pf.write(join(ts_files_relpath, project + '_' + l + '.ts'))

        pf.close()

    def delete(self):

        try:
            os.remove(self._project_file_path)
        except OSError:
            print('There is no project file to delete.')

if __name__ == "__main__":

    # Command line arguments parser
    parser = argparse.ArgumentParser(description='Project file management')
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--create", action="store_true", 
                              help='Create project file {}.pro'.format(project))
    action_group.add_argument("--delete", action="store_true", 
                              help='Delete project file {}.pro'.format(project))
    args = parser.parse_args()

    # Instantiate ProjectFileManager
    pfm = ProjectFileManager()
    
    # Create project file
    if args.create:

        pfm.create()

    # Delete project file
    elif args.delete:

        pfm.delete()

