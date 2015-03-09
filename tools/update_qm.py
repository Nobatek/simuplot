#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from subprocess import call

from projectfile import ProjectFileManager

class QmFilesUpdater(object):

    def __init__(self):

        # Instantiate ProjectFileManager
        self.pfm = ProjectFileManager()

    def update(self):

        # 1/ Create project file
        self.pfm.create()

        # 2 - Update .ts files
        # Assume pylupdate4 is in the path
        # TODO: what about Windows installations ?
        # TODO: lrelease or lrelease-qt4 ?
        try:
            call(['lrelease', self.pfm.file_path])
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                print('[Error] lrelease not found')
            else:
                raise OSError(e)

        # 3 Remove project file
        self.pfm.delete()

if __name__ == "__main__":

    # Instantiate TsFilesUpdater
    qfu = QmFilesUpdater()
 
    # Update ts files
    qfu.update()

