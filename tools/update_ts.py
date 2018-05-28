#!/usr/bin/env python

import os
from subprocess import call

from projectfile import ProjectFileManager

class TsFilesUpdater(object):

    def __init__(self):

        # Instantiate ProjectFileManager
        self.pfm = ProjectFileManager()

    def update(self):

        # 1/ Create project file
        self.pfm.create()

        # 2 - Update .ts files
        # Assume pylupdate5 is in the path
        # TODO: what about Windows installations ?
        try:
            call(['pylupdate5', '-verbose', '-noobsolete', self.pfm.file_path])
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                print('[Error] pylupdate5 not found')
            else:
                raise OSError(e)

        # 3 Remove project file
        self.pfm.delete()

if __name__ == "__main__":

    # Instantiate TsFilesUpdater
    tfu = TsFilesUpdater()

    # Update ts files
    tfu.update()

