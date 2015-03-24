# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os

from PyQt4 import QtCore, QtGui, uic

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
            self.loadSourceTypeSelectBox.addItem(r.name)
            self.loadStackedWidget.addWidget(r)
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
        self.loadSourceTypeSelectBox.activated.connect(
            self.loadStackedWidget.setCurrentIndex)

        # Connect menu signals
        self.copyPlotToClipboardAction.triggered.connect(
            self.copyPlotToClipboard)
        self.copyTableToClipboardAction.triggered.connect(
            self.copyTableToClipboard)

    def setPlotTabsEnabled(self, enable):
        """Enable/disable all plot tabs
        
            enable (bool): Disable or enable plot tabs
        """
        for i in range(self.tabWidget.count()):

            w = self.tabWidget.currentWidget()

            if isinstance(w, dp.dataplotter.DataPlotter):
                self.tabWidget.setTabEnabled(i, enable)

    def copyPlotToClipboard(self):
        """Copy currently displayed plot to Clipboard"""

        w = self.tabWidget.currentWidget()

        # If current tab is a plotter
        # TODO: disable menu action if current tab is not a plotter
        if isinstance(w, dp.dataplotter.DataPlotter):

            pixmap = QtGui.QPixmap.grabWidget(w.plotWidget.canvas)
            self._app.clipboard().setPixmap(pixmap)

    def copyTableToClipboard(self):
        """Copy currently displayed plot's values table to Clipboard"""

        #TODO: copy selected cells only ?

        w = self.tabWidget.currentWidget()

        # If current tab is a plotter
        # TODO: disable menu action if current tab is not a plotter
        if isinstance(w, dp.dataplotter.DataPlotter):

            tw = w.dataTable

            # Create an HTML table from the TableWidget
            html = '<table>'

            # Headers
            html += '<tr>'
            for c in xrange(tw.columnCount()):
                html += '<th>{}</th>'.format(tw.horizontalHeaderItem(c).text())
            html += '</tr>'

            # Data
            for r in xrange(tw.rowCount()):
                html += '<tr>'
                for c in xrange(tw.columnCount()):
                    html += '<td>{}</td>'.format(tw.item(r,c).text())
                html += '</tr>'

            html += '</table>'

            # Cram HTML string into clipboard, setting proper Mime type
            mimeData = QtCore.QMimeData()
            mimeData.setData("text/html", html.encode('utf-8'));
            self._app.clipboard().setMimeData(mimeData)

