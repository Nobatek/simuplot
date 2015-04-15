# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os

from PyQt4 import QtCore, QtGui, uic

from simuplot import UI_PATH, SimuplotError

class DataPlotter(QtGui.QWidget):
    """Virtual class

       Useless by itself. Implement in sub-clases
    """

    # Signals
    warning = QtCore.pyqtSignal(unicode)

    def __init__(self, building, color_chart):

        super(DataPlotter, self).__init__()

        # Reference to building instance
        self._building = building

        # Get color chart
        self._color_chart = color_chart

        # Setup UI
        ui_files_dir = os.path.join(UI_PATH, 'dataplotter')
        ui_file_name = type(self).__name__.lower() + '.ui'
        uic.loadUi(os.path.join(ui_files_dir, ui_file_name), self)

    @QtCore.pyqtSlot()
    def refresh_data(self):
        """Refresh the data list

           Called when data list is populated
        """
        raise NotImplementedError

    @QtCore.pyqtSlot()
    def refresh_plot(self):
        """Refresh the plot"""
        raise NotImplementedError

    @property
    def plot(self):
        """Return the plot as a pixmap"""
        return QtGui.QPixmap.grabWidget(self.plotWidget.canvas)

    @property
    def data(self):
        """Return the table data as an HTML table"""

        #TODO: This is broken if dataTable is not made of QWidgetTableItem only

        tw = self.dataTable

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
                html += '<td>{}</td>'.format(tw.item(r, c).text())
            html += '</tr>'

        html += '</table>'

        return html

class DataPlotterError(SimuplotError):
    pass

