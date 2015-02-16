#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal

from PyQt4 import QtGui, QtCore, uic

from config import Config
from data import Building
from datareader import EnergyPlusDataReader

import dataplotter as dp

class SimuPlot(QtGui.QMainWindow):
    
    def __init__(self):

        super(SimuPlot, self).__init__()

        # Get parameters
        self._config = Config()
        self._config.read()

        # Setup UI
        ui = os.path.join(os.path.dirname(__file__), 'mainwindow.ui')
        self._ui = uic.loadUi(ui, self)

        # Instantiate a Building
        self._building = Building('My Building')

        # Import data
        self._dr = EnergyPlusDataReader(
            self._building,
            self._ui.File_Path_Text,
            self._ui.Info_Load,
            self._ui.progressBar,
            self._ui.Browse_Button,
            self._ui.Ok_Load_Button)

        # Instantiate all plotter widgets and add them as new tabs
        for plot in dp.plotters:
            p = plot(self._building, self._config.params['color_chart'])
            self._dr.dataLoaded.connect(p.refresh_data)
            self._ui.tabWidget.addTab(p, p.name)
        
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

