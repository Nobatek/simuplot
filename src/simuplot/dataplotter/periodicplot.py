# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import QT_TRANSLATE_NOOP as translate

import datetime as dt

import matplotlib.dates as dates

from simuplot.data import SEASONS, TimeInterval
from .dataplotter import DataPlotter, DataPlotterError

# Predefined line style
line_style = ["-","--","-.",":"," "]           

# Predefined marker style
marker_style = [" ","+",",",".","1","2","3","4"]            
           
class PeriodicPlot(DataPlotter):

    def __init__(self, building, color_chart):
        
        super(PeriodicPlot, self).__init__(building, color_chart)
        
        # Plot name
        self._name = self.tr("Time Interval Plotting")

        self._period = None
        
        # Set column number and add headers
        self.dataTable.setColumnCount(7)
        self.dataTable.setHorizontalHeaderLabels([
            self.tr('rm'),
            self.tr('Zone'),
            self.tr('Variable'),
            self.tr('Line style'),
            self.tr('Marker style'),
            self.tr('Show max'),
            self.tr('Show min'),
            ])
        self.dataTable.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)
            
        # Initialise Period radio button to checked
        self.predefinedPeriodCheckBox.setChecked(True)
        
        # Initialise predefinedPeriodComboBox with predefined values
        for dat in SEASONS:
            self.predefinedPeriodComboBox.addItem(dat[0])
        
        # Connect add line button
        self.addButton.clicked.connect(self.AddLine)
        
        # Connect update period signals
        self.predefinedPeriodComboBox.activated.connect(self.update_period)
        self.predefinedPeriodCheckBox.clicked.connect(self.update_period)
        self.customPeriodCheckBox.clicked.connect(self.update_period)
        self.beginDateEdit.dateChanged.connect(self.update_period)
        self.endDateEdit.dateChanged.connect(self.update_period)
        
        self.update_period()
        
    @property
    def name(self):
        return self._name
        
    @QtCore.pyqtSlot()
    def refresh_data(self):
        
        # Get Building zone list (for combobox)
        self._zone_list = self._building.zones
        self._zone_list.sort()
        
        # Check if Environment data are available
        outdoor = self._building.get_environment
        if outdoor is not None:
            self._zone_list.append("Environment")
        
    def AddLine(self):
        # Actual number of row:
        act_row = self.dataTable.rowCount()
        
        # Add one row to table
        #self.dataTable.setRowCount(act_row + 1)
        self.dataTable.insertRow(act_row)
        
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
        
        # Check if it s building zone or environment
        if zone_name in self._building.zones:
            zone = self._building.get_zone(zone_name)
        else:
            zone = self._building.get_environment()
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
        self.dataTable.setCellWidget(act_row, 0, rm_chkbx)
        self.dataTable.setCellWidget(act_row, 1, zone_combo)
        self.dataTable.setCellWidget(act_row, 2, var_combo)
        self.dataTable.setCellWidget(act_row, 3, line_combo)
        self.dataTable.setCellWidget(act_row, 4, marker_combo)
        self.dataTable.setCellWidget(act_row, 5, min_wi)
        self.dataTable.setCellWidget(act_row, 6, max_wi)
        
        # Resize column to fit zone name and variables
        self.dataTable.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)

        # Connect zone combobox to signal to update Available variable for zone 
        zone_combo.activated.connect(self.UpdateVar)
        
        # Connect var, line and marker combobox to signal to update plot
        var_combo.activated.connect(self.refresh_plot)
        line_combo.activated.connect(self.refresh_plot)
        marker_combo.activated.connect(self.refresh_plot)
        
        # Connect rm checkbox to remove the corresponding line
        rm_chkbx.stateChanged.connect(self.RemoveLine)
        
        # Execute load and draw
        self.refresh_plot()

    def RemoveLine(self):
        # Find the table current index
        clickme = QtGui.qApp.focusWidget()
        index = self.dataTable.indexAt(clickme.pos())
        
        # Remove corresponding line
        self.dataTable.removeRow(index.row())
        
        # Call Load and draw
        self.refresh_plot()
    
    def UpdateVar(self):
        # Find the table current index
        clickme = QtGui.qApp.focusWidget()
        index = self.dataTable.indexAt(clickme.pos())

        # Get the zone name
        zone_combo = self.dataTable.cellWidget(index.row(),1)
        zone_name = zone_combo.currentText()
        
        # Check if it s building zone or environment
        if zone_name in self._building.zones :
            zone = self._building.get_zone(zone_name)
        else :
            zone = self._building.get_environment()
        var_list = zone.variables
        
        # Assign variables to the combobox
        # Remove existing variables 
        var_combo = self.dataTable.cellWidget(index.row(),2)
        var_combo.clear()
        
        # Assign new variables 
        for var in var_list:
            var_combo.addItem(var)

        # Update the plot
        self.refresh_plot()
        
    @QtCore.pyqtSlot()
    def update_period(self) :
        """Set self._period from GUI"""
        
        if self.predefinedPeriodCheckBox.isChecked():
            # Predefined periods
            self._period = SEASONS[
                self.predefinedPeriodComboBox.currentIndex()][1]
        else :
            # Custom dates
            self._period = [self.beginDateEdit.date().toString('MM/dd'),
                            self.endDateEdit.date().toString('MM/dd')]
        
        # Update the plot
        self.refresh_plot()
        
    @QtCore.pyqtSlot()    
    def refresh_plot(self):
        
        # TODO: add legend

        # Define canvas
        canvas = self.plotWidget.canvas
        
        # Clear axes
        canvas.axes.cla()      
        canvas.set_tight_layout_on_resize(False)
        
        # If there is at least one data to plot
        if self.dataTable.rowCount():

            # Make TimeInterval from self._period 
            t_interval = TimeInterval.from_string_seq(self._period)
            
            # Go through table to get all variables to plot
            #zone_list = []
            var_list = []
            line_list = []
            marker_list = []
            for i in range(self.dataTable.rowCount()):
                
                # Get zone (or environment) name and add it to list
                zone = self.dataTable.cellWidget(i,1).currentText()
                if zone in self._building.zones:
                    cur_zone = self._building.get_zone(zone)
                else :
                    cur_zone = self._building.get_environment()
                #zone_list.append(cur_zone.name)
                
                # Get variable Array of values for Zone and add it to list
                array = cur_zone.get_array(
                    self.dataTable.cellWidget(i,2).currentText(),'HOUR')
                var_list.append(array.values(t_interval))
                
                # Get line_style and marker style
                line_list.append(self.dataTable.cellWidget(i,3).currentText())
                marker_list.append(self.dataTable.cellWidget(i,4).currentText())
                
            # Create object to handle months days and hours
            months = dates.MonthLocator()
            days = dates.DayLocator()
            hours = dates.HourLocator()
            minutes = dates.MinuteLocator()
            
            # List of hourly dates from start to end
            # TODO: faster with dates.drange ?
            dates_list = dates.date2num(t_interval.get_dt_range('HOUR'))

            # Define x axis
            for var, color, style, mark in zip(var_list,
                                               self._color_chart,
                                               line_list,
                                               marker_list):
                canvas.axes.plot(dates_list,
                                 var,
                                 color = color,
                                 linestyle = style,
                                 marker = mark,
                                 linewidth=2)        
            
            # Format ticks depending on plot delta
            if len(dates_list) <= 48:
                maj_loc = hours
                min_loc = minutes
                fmts = "%H:%M"
            elif len(dates_list) <= 744:
                maj_loc = days
                min_loc = hours
                fmts = "%d-%m"
            else:
                maj_loc = months
                min_loc = days
                fmts = "%d-%m"
            
            # Create a date formatter
            date_fmt = dates.DateFormatter(fmts)
        
            canvas.axes.xaxis.set_major_locator(maj_loc)
            canvas.axes.xaxis.set_major_formatter(date_fmt)
            # canvas.axes.xaxis.set_minor_locator(min_loc)
            canvas.axes.autoscale_view()
            
            # format the coordinates message box
            canvas.axes.fmt_xdata = dates.DateFormatter('%d-%m-%h')
            canvas.axes.grid(True)
            
            canvas.set_tight_layout_on_resize(True)

        # Draw plot
        canvas.draw()      

