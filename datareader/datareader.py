# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

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
        
class DataReaderError(Exception):
    pass

class DataReaderReadError(DataReaderError):
    pass

