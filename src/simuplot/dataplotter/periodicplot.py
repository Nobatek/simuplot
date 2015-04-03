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

from simuplot.data import TimeInterval

from datetime import date, datetime, time, timedelta

import matplotlib.dates as dates

# Predefined period for plot

periods = [(translate('PeriodicPlot', 'Year'),[datetime.strptime('01/01','%m/%d').date(),
                                               datetime.strptime('12/31','%m/%d').date()]),
           (translate('PeriodicPlot', 'Summer'),[datetime.strptime('04/01','%m/%d').date(),
                                               datetime.strptime('09/30','%m/%d').date()]),
           (translate('PeriodicPlot', 'Winter'),[datetime.strptime('10/01','%m/%d').date(),
                                               datetime.strptime('03/31','%m/%d').date()])
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
        
        # Define default value for plot period
        self._period = \
            TimeInterval(periods[self.PeriodCombo.currentIndex()][1])
        
        # Connect Period combobox to refresh_plot
        self.PeriodCombo.activated.connect(self.UpdatePeriod)
        
        # Refresh data when one of the two radio button is switched on or off
        self.period_radio.toggled.connect(self.UpdatePeriod)
        
        # Refresh data when begin date or end date is changed
        self.BeginDate.dateChanged.connect(self.UpdatePeriod)
        self.EndDate.dateChanged.connect(self.UpdatePeriod)
        
        
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
        if outdoor is not None :
            self._zone_list.append("Environment")
    
    
        
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
        
        # Check if it s building zone or environment
        if zone_name in self._building.zones :
            zone = self._building.get_zone(zone_name)
        else :
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
        
        # Check if it s building zone or environment
        if zone_name in self._building.zones :
            zone = self._building.get_zone(zone_name)
        else :
            zone = self._building.get_environment()
        var_list = zone.variables
        
        # Assign variables to the combobox
        # Remove existing variables 
        var_combo = self._table_widget.cellWidget(index.row(),2)
        var_combo.clear()
        
        # Assign new variables 
        for var in var_list:
            var_combo.addItem(var)

        # Update the plot
        self.refresh_plot()
        
    def UpdatePeriod(self) :
        # Get the period depending on radio chosen option
        # Get begin and end datetime for plot axis
        if self.period_radio.isChecked():
            self._period = \
                TimeInterval(periods[self.PeriodCombo.currentIndex()][1])
        else :
            # Get end_date and begin_date from the interface calendar
            begin_date = self.BeginDate.date()
            end_date = self.EndDate.date()
            
            # Convert Qdatetime object begin_date into date object            
            year, month, day = begin_date.getDate()
            begin_date = date(year, month, day)
            
            # Convert Qdatetime object end_date into date object
            year, month, day = end_date.getDate()
            end_date = date(year, month, day)
            
            # Create the TimeInterval object
            self._period = TimeInterval([begin_date,end_date])
        
        # Update the plot
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
            # Get zone or environment from Combobox and add it to list
            zone_combo = self._table_widget.cellWidget(i,1)
            zone_name = zone_combo.currentText()
            if zone_name in self._building.zones:
                cur_zone = self._building.get_zone(zone_name)
            else :
                cur_zone = self._building.get_environment()
            
            zone_list.append(cur_zone.name)
            
            # Get variable values for zone and add it to list
            var_combo = self._table_widget.cellWidget(i,2)
            # Get the variable Array
            cur_var = cur_zone.get_values(var_combo.currentText(),'HOUR')
            
            # Get the Array set corresponding to the TimeInterval 
            var_in_period = cur_var.get_interval(self._period)
                
            # Add the Array set to the list of variable
            var_list.append(var_in_period)
            
            # Get line_style 
            line_combo = self._table_widget.cellWidget(i,3)
            line_list.append(line_combo.currentText())
            
            # Get marker style 
            marker_combo = self._table_widget.cellWidget(i,4)
            marker_list.append(marker_combo.currentText())
            
        # Create object to handle months days and hours
        months = dates.MonthLocator()
        days = dates.DayLocator()
        hours = dates.HourLocator()
        minutes = dates.MinuteLocator()
        
        # Get a list of datetime for the interval in period        
        dates_list = self._period.get_datetimelist()
        
        # Reformat dates_list before plotting
        dates_list = [dates.date2num(dat) for dat in dates_list]
        
        #define the x axes
        for var, color, style, mark in zip(var_list,
                                           self._color_chart,
                                           line_list,
                                           marker_list):
            
            print ("dates_list = ", len(dates_list))
            print ("size de var = ", var.size)
            
            canvas.axes.plot(dates_list,
                             var,
                             color = color,
                             linestyle = style,
                             marker = mark,
                             linewidth=2)        
        
        # format the ticks depending on plot delta
        if len(dates_list) <= 48 :
            maj_loc = hours
            min_loc = minutes
            fmts = "%H:%M"
        elif len(dates_list) <= 744 :
            maj_loc = days
            min_loc = hours
            fmts = "%d-%m"
        else :
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
        
        # Draw plot
        canvas.draw()      
     
