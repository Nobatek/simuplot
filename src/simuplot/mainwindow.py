# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os

from PyQt4 import QtGui, uic

from . import ui_path
from . import datareader as dr
from . import dataplotter as dp

from .config import Config
from .statusbar import StatusBar
from .data import Building

class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, app):

        super(MainWindow, self).__init__()

        # Application
        self._app = app

        # Get parameters
        self._config = Config()
        self._config.read()

        # Setup UI
        uic.loadUi(os.path.join(ui_path, 'mainwindow.ui'), self)

        # Setup status bar
        self.setStatusBar(StatusBar())

        # Instantiate a Building
        self._building = Building('My Building')

        # Instantiate all plotter widgets and add them as new tabs
        plotters = []
        for plotter in dp.plotters:
            p = plotter(self._building, self._config.params['color_chart'])
            plotters.append(p)
            self.tabWidget.addTab(p, p.name)
            # Connect signals to status bar
            p.warning.connect(self.statusBar().warning)

        # Disable all plotter tabs
        self.setPlotTabsEnabled(False)

        # Instantiate all reader widgets and add them to stacked widget
        for reader in dr.readers:
            r = reader(self._building)
            self.comboBox.addItem(r.name)
            self.stackedWidget.addWidget(r)
            # Connect signals to status bar
            r.loadingData.connect(self.statusBar().loadingData)
            r.dataLoaded.connect(self.statusBar().dataLoaded)
            r.dataLoadError.connect(self.statusBar().dataLoadError)
            r.dataLoadProgress.connect(self.statusBar().dataLoadProgress)
            # Connect signals to all plotters
            for p in plotters:
                r.dataLoaded.connect(p.refresh_data)
                r.dataLoadError.connect(p.refresh_data)
            # Enable or disable tabs depending on load status
            r.dataLoaded.connect(lambda: self.setPlotTabsEnabled(True))
            r.dataLoadError.connect(lambda: self.setPlotTabsEnabled(False))

        # Connect comboBox activated signal to stackedWidget set index slot
        self.comboBox.activated.connect(
            self.stackedWidget.setCurrentIndex)

        # Connect menu signals
        self.actionCopyPlotToClipboard.triggered.connect(
            self.copyPlotToClipboard)

    def setPlotTabsEnabled(self, enable):
        """Enable/disable all plot tabs
        
            enable (bool): Disable or enable plot tabs
        """
        for i in range(self.tabWidget.count()):

            w = self.tabWidget.currentWidget()

            if isinstance(w, dp.DataPlotter):
                self.tabWidget.setTabEnabled(i, enable)

    def copyPlotToClipboard(self):
        """Copy currently displayed plot to Clipboard"""

        w = self.tabWidget.currentWidget()

        # Current tab is not a plotter
        if not isinstance(w, dp.DataPlotter):
            return

        pixmap = QtGui.QPixmap.grabWidget(w.plotW.canvas)
        self._app.clipboard().setPixmap(pixmap)

