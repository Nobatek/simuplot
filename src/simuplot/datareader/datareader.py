# -*- coding: utf-8 -*-

import os

from PyQt4 import QtCore, QtGui, uic

from simuplot import ui_path 

ui_files_dir = os.path.join(ui_path, 'datareader')

class DataReader(QtGui.QWidget):
    
    # Signals
    # Before loading data
    loadingData = QtCore.pyqtSignal(str)
    # When data is successfully loaded
    dataLoaded = QtCore.pyqtSignal(str)
    # When an error occurred while loading data
    dataLoadError = QtCore.pyqtSignal(str)
    # Data loading progress
    dataLoadProgress = QtCore.pyqtSignal(int)
    
    def __init__(self, building):

        super(DataReader, self).__init__()
        
        # Building isntance
        self._building = building

        # Setup UI
        ui_file_name = type(self).__name__.lower() + '.ui'
        uic.loadUi(os.path.join(ui_files_dir, ui_file_name), self)

class DataReaderError(Exception):
    pass

class DataReaderReadError(DataReaderError):
    pass

