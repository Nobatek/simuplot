# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import QT_TRANSLATE_NOOP as translate

import numpy as np

import matplotlib.pyplot as plt

from .dataplotter import DataPlotter, DataPlotterError

from data import DataZoneError


# Predefined period for plot

periods = [(translate('PeriodicPlot', 'Year'),[["Jan-Dec"],]),
           (translate('PeriodicPlot', 'Summer'),[["Apr-Sep"]]),
           (translate('PeriodicPlot', 'Winter'),[["Jan-Mar","Oct-Dec"]]),
           ]
           
# Predefined line style
line_style = ["-","--","-.",":"," "]           

# Predefined marker style
marker_style = ["+",",",".","1","2","3","4"]            
           
class PeriodicPlot(DataPlotter):

    def __init__(self, building, color_chart):
        
        super(PeriodicPlot, self).__init__(building, color_chart)
        
        # Plot name
        self._name = self.tr("Time Interval Plotting")
        
        # Chart and table widgets
        self._MplWidget = self.plotW
        self._table_widget = self.listW
        
        # Set column number and add headers
        self._table_widget.setColumnCount(7)
        self._table_widget.setHorizontalHeaderLabels([
            self.tr('rm'),
            self.tr('Zone'),
            self.tr('Variable'),
            self.tr('Line style'),
            self.tr('Marker style'),
            self.tr('Show max'),
            self.tr('Show min'),
            ])


        # Connect browse and load buttons
        self.AddButton.clicked.connect(self.AddLine)
        
        # Refresh plot when zone is clicked/unclicked or sort order changed
        # self._table_widget.cellClicked.connect(self.PrintCurrent)
        
    @property
    def name(self):
        return self._name
        
    @QtCore.pyqtSlot()
    def refresh_data(self):
        # Get Building zone list (for combobox)
        self._zone_list = self._building.zones
        self._zone_list.sort()
    
    
        
    def AddLine(self):
        # Actual number of row:
        act_row = self._table_widget.rowCount()
        
        # Add one row to table
        self._table_widget.setRowCount(act_row + 1)
        
        # Creates the zone combobox
        zone_combo = QtGui.QComboBox()
        # Initialise zone names in combobox
        for zname in self._zone_list:
            zone_combo.addItem(zname)
            
        # Create the variable combobox
        var_combo = QtGui.QComboBox()
        
        # Initialise variable in combobox
        # First get the current zone variables
        zone_name = zone_combo.currentText()
        zone = self._building.get_zone(zone_name)
        var_list = zone.variables
        
        # Assign variables to variable combobox
        for var in var_list:
            var_combo.addItem(var)     

        # Initialise line style combobox
        line_combo = QtGui.QComboBox()
        for dat in line_style :
            line_combo.addItem(dat)
        
        # Initialise marker combobox
        marker_combo = QtGui.QComboBox()
        for dat in marker_style :
            marker_combo.addItem(dat)
            
        # Initialize check boxes for rm, min, max
        rm_item = QtGui.QCheckBox()
        min_item = QtGui.QCheckBox()
        max_item = QtGui.QCheckBox()
                    
        
        # Add combobox and check boxes to the table
        self._table_widget.setCellWidget(act_row, 1, zone_combo)
        self._table_widget.setCellWidget(act_row, 2, var_combo)
        self._table_widget.setCellWidget(act_row, 3, line_combo)
        self._table_widget.setCellWidget(act_row, 4, marker_combo)
        self._table_widget.setCellWidget(act_row, 0, rm_item)
        self._table_widget.setCellWidget(act_row, 5, min_item)
        self._table_widget.setCellWidget(act_row, 6, max_item)
        
        # Connect combobox to signal to update Available variable for zone 
        zone_combo.activated.connect(self.UpdateVar)
        
        # Connect rm checkbox to remove the corresponding line
        rm_item.stateChanged.connect(self.RemoveLine)

    def RemoveLine(self):
        # Find the table current index
        clickme = QtGui.qApp.focusWidget()
        index = self._table_widget.indexAt(clickme.pos())
        
        # Remove corresponding line
        self._table_widget.removeRow(index.row())
    
    def UpdateVar(self):
        # Find the table current index
        clickme = QtGui.qApp.focusWidget()
        index = self._table_widget.indexAt(clickme.pos())

        # Get the zone name
        zone_combo = self._table_widget.cellWidget(index.row(),1)
        zone_name = zone_combo.currentText()
        
        # Get the list of variables available for the zone
        zone = self._building.get_zone(zone_name)
        var_list = zone.variables
        
        # Assign variables to the combobox
        # Remove existing variables 
        var_combo = self._table_widget.cellWidget(index.row(),2)
        var_combo.clear()
        
        # Assign new variables 
        for var in var_list:
            var_combo.addItem(var)
            
    def RefreshPlot(self):
        return 0
        
        

        
        
        
        
        
        
        
     
