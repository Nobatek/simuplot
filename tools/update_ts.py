#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import call

from projectfile import ProjectFileManager

class TsFilesUpdater(object):

    def __init__(self):

        # Instantiate ProjectFileManager
        self.pfm = ProjectFileManager()

    def update(self):

        # 1/ Create project file
        self.pfm.create()

        # 2 - Update .ts files
        # Assume pylupdate4 is in the path
        # TODO: what about Windows installations ?
        # TODO: check pylupdate4 is installed
        call(['pylupdate4', self.pfm.file_path])

        # 3 Remove project file
        self.pfm.delete()

if __name__ == "__main__":

    # Instantiate TsFilesUpdater
    tfu = TsFilesUpdater()
 
    # Update ts files
    tfu.update()

