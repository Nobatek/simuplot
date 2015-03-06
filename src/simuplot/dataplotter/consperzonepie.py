# -*- coding: utf-8 -*-
from __future__ import division

from PyQt4 import QtCore, QtGui

import numpy as np

from .dataplotter import DataPlotter, DataPlotterError

from simuplot.data import DataZoneError

class ConsPerZonePie(DataPlotter):

    @staticmethod
    def ComputeZoneCons(zone):
        try:
            # Get variable HEATING_RATE in zone
            # Hourly power [W] is equivalent to Hourly energy [Wh]
            vals = zone.get_values('HEATING_RATE', 'HOUR')
        except DataZoneError:
            # TODO: log warning
            return 0
        else:
            # Return total heat need [kWh]
            return vals.sum() / 1000
        
    def __init__(self, building, color_chart):
        
        super(ConsPerZonePie, self).__init__(building, color_chart)

        self._name = "Energy heat need per zone"
        
        # Initialize total building heat need
        self._build_total_hn = 0
        
        # Chart widget
        self._MplWidget = self.plotW
        # Table widget
        self._table_widget = self.listW

        # Set column number and add headers
        self._table_widget.setColumnCount(2)
        self._table_widget.setHorizontalHeaderLabels(['Zone', 
                                                      'Heat need [kWh]'])
        self._table_widget.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)
 
        # Refresh plot when zone is clicked/unclicked or sort order changed
        self._table_widget.itemClicked.connect(self.refresh_plot)
        self._table_widget.horizontalHeader().sectionClicked.connect(
            self.refresh_plot)

    @property
    def name(self):
        return self._name

    @QtCore.pyqtSlot()
    def refresh_data(self):
    
        # Reset total building heat need
        self._build_total_hn = 0
        
        # Get zones in building
        zones = self._building.zones
        
        # Clear table and disable sorting before populating the table
        self._table_widget.clearContents()
        self._table_widget.setSortingEnabled(False)

        # Create one empty row per zone
        self._table_widget.setRowCount(len(zones))
        
        # For each zone
        for i, name in enumerate(zones):

            # Compute total heat need
            # TODO: int or float ? explicit rounding ?
            cons = int(self.ComputeZoneCons(self._building.get_zone(name)))
            self._build_total_hn += cons

            # Firts column: zone name + checkbox
            name_item = QtGui.QTableWidgetItem(name)

            name_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                               QtCore.Qt.ItemIsEnabled)

            # By default, display zone on chart only if value not 0
            if cons != 0:
                name_item.setCheckState(QtCore.Qt.Checked)
            else:
                name_item.setCheckState(QtCore.Qt.Unchecked)

            # Second column: heat need value
            val_item = QtGui.QTableWidgetItem()
            val_item.setData(QtCore.Qt.DisplayRole, cons)
            
            val_item.setFlags(QtCore.Qt.ItemIsEnabled)

            # Add items to row, column
            self._table_widget.setItem(i, 0, name_item)
            self._table_widget.setItem(i, 1, val_item)
            
        # Sort by value, descending order, and allow user column sorting
        self._table_widget.sortItems(1, QtCore.Qt.DescendingOrder)
        self._table_widget.setSortingEnabled(True)        

        # Draw plot
        self.refresh_plot()

    @QtCore.pyqtSlot()
    def refresh_plot(self):

        values = []
        names = []
        
        canvas = self._MplWidget.canvas

        # Get checked rows and corresponding (name, value)
        for i in range(self._table_widget.rowCount()):
            if self._table_widget.item(i,0).checkState() == QtCore.Qt.Checked:
                name = self._table_widget.item(i,0).text()
                names.append(name)
                try:
                    value = int(self._table_widget.item(i,1).text())
                except AttributeError:
                    raise DataPlotterError(
                        'Invalid cons value type for row {} ({}): {}'
                        ''.format(i, name, self._table_widget.item(i,1)))
                except ValueError:
                    raise DataPlotterError(
                        'Invalid cons value for row {} ({}): {}'
                        ''.format(i, name, self._table_widget.item(i,1).text()))
                else:
                    values.append(value)
            
        # Clear axes
        canvas.axes.cla()
    
        # Create pie chart
        # (Make zone heat need non dimensional to avoid pie expansion)
        canvas.axes.pie(np.array(values) / self._build_total_hn, 
                        labels=names,
                        colors=self._color_chart, autopct='%1.1f%%', 
                        shadow=False, startangle=90)
        canvas.axes.axis('equal')
        
        # Set title
        title_str = 'Building heat need : {} [kWh]'.format(self._build_total_hn)
        title = canvas.axes.set_title(title_str, y = 1.05)
        
        # Draw plot
        canvas.draw()

