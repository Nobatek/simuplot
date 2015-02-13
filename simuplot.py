#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal

from PyQt4 import QtGui, QtCore, uic

from config import Config
from data import Building
from datareader import EnergyPlusDataReader
from dataplotter import ConsPerZonePieDataPlotter

class SimuPlot(QtGui.QMainWindow):
    
    def __init__(self):

        super(SimuPlot, self).__init__()

        # Get parameters
        self._config = Config()
        self._config.read()

        # Setup UI
        ui = os.path.join(os.path.dirname(__file__), 'mainwindow.ui')
        self._ui = uic.loadUi(ui, self)

        # Instanciate a Building
        self._building = Building('My Building')

        # Import data
        self._dr = EnergyPlusDataReader(
            self._building,
            self._ui.File_Path_Text,
            self._ui.Info_Load,
            self._ui.progressBar,
            self._ui.Browse_Button,
            self._ui.Ok_Load_Button)

        # Tab 1: Consumption per zone / Pie
        self.tab1 = ConsPerZonePieDataPlotter(
            self._ui.MplWidget,
            self._ui.table_Con_Zon,
            self._building,
            self._config.params['color_chart'])

        # Catch dataLoaded signal
        self._dr.dataLoaded.connect(self.data_loaded)

    @QtCore.pyqtSlot()
    def data_loaded(self):
        """Executes when data was loaded"""
        
        # Refresh data in tabs
        self.tab1.refresh_data()

if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)

    # Let the interpreter run each 100 ms to catch SIGINT.
    signal.signal(signal.SIGINT, lambda *args : app.quit())
    timer = QtCore.QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)  

    mySW = SimuPlot()
    mySW.show()

    sys.exit(app.exec_())

