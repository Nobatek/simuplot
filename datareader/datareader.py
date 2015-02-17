# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

class DataReader(QtGui.QWidget):
    
    # This signal is sent when data is successfully loaded
    # TODO: check what happens in case of load failure
    dataLoaded = QtCore.pyqtSignal()
    
    def __init__(self, building):

        super(DataReader, self).__init__()
        
        # Building isntance
        self._building = building
        
class DataReaderError(Exception):
    pass

class DataReaderReadError(DataReaderError):
    pass

