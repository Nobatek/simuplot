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

periods = [(translate('PeriodicPlot', 'Year'),["Jan-Dec"]),
           (translate('PeriodicPlot', 'Summer'),["Apr-Sep"]),
           (translate('PeriodicPlot', 'Winter'),["Jan-Mar","Oct-Dec"]),
           ]
           
# Predefined line style
line_style = ["-","--","-.",":"," "]           

# Predefined marker style
marker_style = [" ","+",",",".","1","2","3","4"]            
           
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
        self._table_widget.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)
            
        # Initialise Period radio button to checked
        self.period_radio.setChecked(True)
        
        # Initialise PeriodCombo with predefined values
        for dat in periods:
            self.PeriodCombo.addItem(dat[0])
        
        # Connect add line button
        self.AddButton.clicked.connect(self.AddLine)
        
        # Connect Period combobox to refresh_plot
        self.PeriodCombo.activated.connect(self.refresh_plot)
        
        # Refresh data when one of the two radio button is switched on or off
        self.period_radio.toggled.connect(self.refresh_plot)
        
        # Refresh data when begin date or end date is changed
        self.BeginDate.dateChanged.connect(self.refresh_plot)
        self.EndDate.dateChanged.connect(self.refresh_plot)
        
        
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

        
        # Create check box for rm (remove line)
        rm_chkbx = QtGui.QCheckBox()
        
        # Create checkbox and layout for min and max
        # Create the checkbox
        min_chkbx = QtGui.QCheckBox()
        max_chkbx = QtGui.QCheckBox()
        # Create the global widget
        min_wi = QtGui.QWidget()
        max_wi = QtGui.QWidget()
        # Create a layout for the widget
        min_lay = QtGui.QHBoxLayout(min_wi)
        max_lay = QtGui.QHBoxLayout(max_wi)
        # Add the checkbox to the layout 
        min_lay.addWidget(min_chkbx)
        max_lay.addWidget(max_chkbx)
        # Align the checkbox in the layout
        min_lay.setAlignment(QtCore.Qt.AlignCenter)
        max_lay.setAlignment(QtCore.Qt.AlignCenter)
        
        # Add combobox and check boxes to the table        
        self._table_widget.setCellWidget(act_row, 1, zone_combo)
        self._table_widget.setCellWidget(act_row, 2, var_combo)
        self._table_widget.setCellWidget(act_row, 3, line_combo)
        self._table_widget.setCellWidget(act_row, 4, marker_combo)
        self._table_widget.setCellWidget(act_row, 0, rm_chkbx)
        self._table_widget.setCellWidget(act_row, 5, min_wi)
        self._table_widget.setCellWidget(act_row, 6, max_wi)
        
        # Resize column to fit zone name and variables
        self._table_widget.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)

        # Execute load and draw
        self.refresh_plot()
        
        # Connect zone combobox to signal to update Available variable for zone 
        zone_combo.activated.connect(self.UpdateVar)
        
        # Connect var, line and marker combobox to signal to update plot
        var_combo.activated.connect(self.refresh_plot)
        line_combo.activated.connect(self.refresh_plot)
        marker_combo.activated.connect(self.refresh_plot)
        
        # Connect rm checkbox to remove the corresponding line
        rm_chkbx.stateChanged.connect(self.RemoveLine)
        


    def RemoveLine(self):
        # Find the table current index
        clickme = QtGui.qApp.focusWidget()
        index = self._table_widget.indexAt(clickme.pos())
        
        # Remove corresponding line
        self._table_widget.removeRow(index.row())
        
        # Call Load and draw
        self.refresh_plot()
    
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

        # Call Load and draw
        self.refresh_plot()
    
    @QtCore.pyqtSlot()    
    def refresh_plot(self):
        
        # Initialize list of zone to plot
        zone_list = []
        
        # Initialise corresponding Variable list
        var_list = []
        
        # Initialise list of line style
        line_list = []
        
        # Initialise list of marker
        marker_list = []
        
        # Define canvas
        canvas = self._MplWidget.canvas
        
        # Clear axes
        canvas.axes.cla()
        
        # Go through table
        for i in range(self._table_widget.rowCount()):
            # Get zone name and add it to list
            zone_combo = self._table_widget.cellWidget(i,1)
            cur_zone = self._building.get_zone(zone_combo.currentText())
            zone_list.append(cur_zone.name)
            
            # Get variable values for zone and add it to list
            var_combo = self._table_widget.cellWidget(i,2)
            # Get the variable Array
            cur_var = cur_zone.get_values(var_combo.currentText(),'HOUR')
            
            # Get the time interval to plot values
            if self.period_radio.isChecked():
                time_interval = \
                    periods[self.PeriodCombo.currentIndex()][1]
            else :
                begin_date = self.BeginDate.date()
                end_date = self.EndDate.date()
                time_interval = [begin_date.toString("MM/dd")+"-"+
                                 end_date.toString("MM/dd")]
            
            print (time_interval)
            
            # Get the Array set corresponding to the interval 
            #(or combine intervals if 2 period in interval eg. winter)
            var_in_interval = np.array([])
            for per in time_interval :
                var_in_interval = np.concatenate( \
                (var_in_interval,cur_var.get_interval(per)),axis = 0)
                

            
            # Add the Array full set to the list of variable
            var_list.append(var_in_interval)
            
            # Get line_style 
            line_combo = self._table_widget.cellWidget(i,3)
            line_list.append(line_combo.currentText())
            
            # Get marker style 
            marker_combo = self._table_widget.cellWidget(i,4)
            marker_list.append(marker_combo.currentText())
        
        #define the x axes
        for var, color, style, mark in zip(var_list,
                                           self._color_chart,
                                           line_list,
                                           marker_list):
            canvas.axes.plot(var,
                             color = color,
                             linestyle = style,
                             marker = mark,
                             linewidth=2)
        
        # Draw plot
        canvas.draw()      
     
