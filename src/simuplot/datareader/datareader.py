# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

import os

from PyQt4 import QtCore, QtGui, uic

from simuplot import ui_path, SimuplotError
from simuplot.data import DataTypes

ui_files_dir = os.path.join(ui_path, 'datareader')

def F_to_C(val):
    return (val - 32) * 5 / 9

def J_to_Wh(val):
    return val * 2.78e-4

def J_to_kWh(val):
    return val * 2.78e-7

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
    
    # Unit conversions
    # If expected unit is provided, conversion is identity
    # DataTypes is a dict of type:(unit, string)
    conversions = {data_type:{data_props[0]:lambda x:x}
        for data_type, data_props in DataTypes.iteritems()}
    # Otherwise, specify conversion
    conversions['AIR_DRYBULB_TEMPERATURE']['°F'] = F_to_C
    conversions['AIR_WETBULB_TEMPERATURE']['°F'] = F_to_C
    conversions['OPERATIVE_TEMPERATURE']['°F'] = F_to_C
    conversions['INFILTRATION_HEATING_RATE']['J'] = J_to_Wh

    def __init__(self, building):

        super(DataReader, self).__init__()
        
        # Building isntance
        self._building = building

        # Setup UI
        ui_file_name = type(self).__name__.lower() + '.ui'
        uic.loadUi(os.path.join(ui_files_dir, ui_file_name), self)

class DataReaderError(SimuplotError):
    pass

class DataReaderReadError(DataReaderError):
    pass

