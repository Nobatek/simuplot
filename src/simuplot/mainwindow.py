# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os

from PyQt4 import QtCore, QtGui, uic

from . import UI_PATH
from . import datareader as dr
from . import dataplotter as dp

from .config import Config
from .statusbar import StatusBar
from .data import Building

class MainWindow(QtGui.QMainWindow):

    def __init__(self, app):

        super(MainWindow, self).__init__()

        # Application
        self._app = app

        # Get parameters
        self._config = Config()
        self._config.read()

        # Setup UI
        uic.loadUi(os.path.join(UI_PATH, 'mainwindow.ui'), self)

        # Setup status bar
        self.setStatusBar(StatusBar())

        # Instantiate a Building
        self._building = Building('My Building')

        # Instantiate all plotter widgets and add them as new tabs
        plotters = []
        for plotter in dp.PLOTTERS:
            p = plotter(self._building, self._config.params['color_chart'])
            plotters.append(p)
            self.tabWidget.addTab(p, p.name)
            # Connect signals to status bar
            p.warning.connect(self.statusBar().warning)

        # Disable all plotter tabs
        self.set_plot_tabs_enabled(False)

        # Instantiate all reader widgets and add them to stacked widget
        for reader in dr.READERS:
            r = reader(self._building)
            self.loadSourceTypeSelectBox.addItem(r.name)
            self.loadStackedWidget.addWidget(r)
            # Connect signals to status bar
            r.loadingData.connect(self.statusBar().loadingData)
            r.dataLoaded.connect(self.statusBar().dataLoaded)
            r.dataLoadError.connect(self.statusBar().dataLoadError)
            r.dataLoadProgress.connect(self.statusBar().dataLoadProgress)
            # Connect signals to all plotters
            for p in plotters:
                r.dataLoaded.connect(p.refresh_data)
                r.dataLoadError.connect(p.refresh_data)
            # Enable or disable tabs depending on load status
            r.dataLoaded.connect(lambda: self.set_plot_tabs_enabled(True))
            r.dataLoadError.connect(lambda: self.set_plot_tabs_enabled(False))

        # Connect comboBox activated signal to stackedWidget set index slot
        self.loadSourceTypeSelectBox.activated.connect(
            self.loadStackedWidget.setCurrentIndex)

        # Connect menu signals
        self.copyPlotToClipboardAction.triggered.connect(
            self.copy_plot_to_clipboard)
        self.copyTableToClipboardAction.triggered.connect(
            self.copy_table_to_clipboard)

        # Connect tab selection changed signal
        self.tabWidget.currentChanged.connect(self.tab_selection_changed)

    def set_plot_tabs_enabled(self, enable):
        """Enable/disable all plot tabs

            enable (bool): Disable or enable plot tabs
        """

        for i in range(self.tabWidget.count()):

            w = self.tabWidget.widget(i)

            if isinstance(w, dp.dataplotter.DataPlotter):
                self.tabWidget.setTabEnabled(i, enable)

    @QtCore.pyqtSlot()
    def tab_selection_changed(self):

        # Enable copy(Plot|Table)ToClipboard if and only if
        # selected widget is a DataPlotter
        w = self.tabWidget.currentWidget()
        enable = isinstance(w, dp.dataplotter.DataPlotter)
        self.copyPlotToClipboardAction.setEnabled(enable)
        self.copyTableToClipboardAction.setEnabled(enable)

    @QtCore.pyqtSlot()
    def copy_plot_to_clipboard(self):
        """Copy currently displayed plot to clipboard"""

        w = self.tabWidget.currentWidget()

        # If current tab is a plotter
        # TODO: disable menu action if current tab is not a plotter
        if isinstance(w, dp.dataplotter.DataPlotter):
            self._app.clipboard().setPixmap(w.plot)

    @QtCore.pyqtSlot()
    def copy_table_to_clipboard(self):
        """Copy currently displayed plot's values table to clipboard"""

        w = self.tabWidget.currentWidget()

        # If current tab is a plotter
        # TODO: disable menu action if current tab is not a plotter
        if isinstance(w, dp.dataplotter.DataPlotter):

            # Cram HTML string into clipboard, setting proper Mime type
            html_table = w.data
            if html_table is None:
                self._app.clipboard().clear()
            else:
                mimeData = QtCore.QMimeData()
                mimeData.setData("text/html", html_table.encode('utf-8'))
                self._app.clipboard().setMimeData(mimeData)

