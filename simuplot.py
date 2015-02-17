#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal

from PyQt4 import QtCore, QtGui, uic

from config import Config
from data import Building

import datareader as dr
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

        # Instantiate all reader widgets and add them to stacked widget
        readers = []
        for reader in dr.readers:
            r = reader(self._building)
            readers.append(r)
            self.comboBox.addItem(r.name)
            self._ui.stackedWidget.addWidget(r)

        # Connect comboBox activated signal to stackedWidget set index slot
        self._ui.comboBox.activated.connect( \
            self._ui.stackedWidget.setCurrentIndex)

        # Instantiate all plotter widgets and add them as new tabs
        for plotter in dp.plotters:
            p = plotter(self._building, self._config.params['color_chart'])
            self._ui.tabWidget.addTab(p, p.name)
            # Connect dataLoaded signal of all readers to the plotter
            for r in readers:
                r.dataLoaded.connect(p.refresh_data)
        
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

