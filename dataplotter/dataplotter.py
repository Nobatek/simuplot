# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

class DataPlotter(QtGui.QWidget):
    """Virtual class

       Useless by itself. Implement in sub-clases
    """
    
    def __init__(self, building, color_chart):
        
        super(DataPlotter, self).__init__()

        # Reference to building instance
        self._building = building

        # Get color chart
        self._color_chart = color_chart

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

