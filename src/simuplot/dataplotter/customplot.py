# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


from PyQt4 import QtCore, QtGui

import datetime as dt

import matplotlib.dates as dates

from simuplot.data import SEASONS, TimeInterval
from .dataplotter import DataPlotter, DataPlotterError

# Predefined line style
line_style = ["-","--","-.",":"," "]           

# Predefined marker style
marker_style = [" ","+",",",".","1","2","3","4"]            
           
class CustomPlot(DataPlotter):

    def __init__(self, building, color_chart):
        
        super(CustomPlot, self).__init__(building, color_chart)
        
        # Plot name
        self._name = self.tr("Time Interval Plotting")

        self._period = None
        
        # Set column number and add headers
        self.dataTable.setColumnCount(5)
        self.dataTable.setHorizontalHeaderLabels([
            '',
            self.tr('Zone'),
            self.tr('Variable'),
            self.tr('Line style'),
            self.tr('Marker style'),
#            self.tr('Show max'),
#            self.tr('Show min'),
            ])
        self.dataTable.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)
            
        # Set predefined period as default
        self.predefinedPeriodCheckBox.setChecked(True)
        
        # Initialise predefinedPeriodComboBox with predefined values
        for dat in SEASONS:
            self.predefinedPeriodComboBox.addItem(dat[0])
        
        # Connect "add row" button
        self.addButton.clicked.connect(self._addRow)
        
        # Connect update period signals
        self.predefinedPeriodComboBox.activated.connect(self.refresh_plot)
        self.predefinedPeriodCheckBox.clicked.connect(self.refresh_plot)
        self.customPeriodCheckBox.clicked.connect(self.refresh_plot)
        self.beginDateEdit.dateChanged.connect(self.refresh_plot)
        self.endDateEdit.dateChanged.connect(self.refresh_plot)
        
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
        
        # Remove all rows from dataTable
        self.dataTable.clearContents()

    def _addRow(self):
        
        # Insert row at bottom of dataTable
        row_index = self.dataTable.rowCount()
        self.dataTable.insertRow(row_index)
        
        # Get persistent row index
        # (http://stackoverflow.com/questions/29633311/)
        index = QtCore.QPersistentModelIndex(
            self.dataTable.model().index(row_index, 0))
        
        # Initialize Zone combobox
        zone_combo = QtGui.QComboBox()
        for zname in self._zone_list:
            zone_combo.addItem(zname)
            
        # Create Variable combobox
        var_combo = QtGui.QComboBox()

        # Initialise line style combobox
        line_combo = QtGui.QComboBox()
        for dat in line_style :
            line_combo.addItem(dat)
        
        # Initialise marker combobox
        marker_combo = QtGui.QComboBox()
        for dat in marker_style :
            marker_combo.addItem(dat)
            
        # Create "remove row" Button
        rm_button = QtGui.QPushButton()
        rm_button.setIcon(QtGui.qApp.style().standardIcon(
            QtGui.QStyle.SP_DialogDiscardButton))

# Remove this until min and max are implemented
#         # Create checkbox and layout for min and max
#         # Create the checkbox
#         min_chkbx = QtGui.QCheckBox()
#         max_chkbx = QtGui.QCheckBox()
#         # Create the global widget
#         min_wi = QtGui.QWidget()
#         max_wi = QtGui.QWidget()
#         # Create a layout for the widget
#         min_lay = QtGui.QHBoxLayout(min_wi)
#         max_lay = QtGui.QHBoxLayout(max_wi)
#         # Add the checkbox to the layout 
#         min_lay.addWidget(min_chkbx)
#         max_lay.addWidget(max_chkbx)
#         # Align the checkbox in the layout
#         min_lay.setAlignment(QtCore.Qt.AlignCenter)
#         max_lay.setAlignment(QtCore.Qt.AlignCenter)

        # Add items to table row
        self.dataTable.setCellWidget(row_index, 0, rm_button)
        self.dataTable.setCellWidget(row_index, 1, zone_combo)
        self.dataTable.setCellWidget(row_index, 2, var_combo)
        self.dataTable.setCellWidget(row_index, 3, line_combo)
        self.dataTable.setCellWidget(row_index, 4, marker_combo)
#         self.dataTable.setCellWidget(act_row, 5, min_wi)
#         self.dataTable.setCellWidget(act_row, 6, max_wi)

        # Resize column to fit zone name and variables
        self.dataTable.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)

        # Update Variables when Zone changed
        zone_combo.activated.connect(lambda: self._updateVariable(index))
        
        # Refresh plot when Variable, line style or marker style changed
        var_combo.activated.connect(self.refresh_plot)
        line_combo.activated.connect(self.refresh_plot)
        marker_combo.activated.connect(self.refresh_plot)
        
        # Remove row when rm Button clicked
        rm_button.clicked.connect(lambda: self._removeLine(index))
        
        # Set variables according to selected zone
        self._updateVariable(index)

    def _removeLine(self, index):
        
        if index.isValid():
        
            # Remove corresponding row 
            self.dataTable.removeRow(index.row())

            # Call Load and draw
            self.refresh_plot()
    
    def _updateVariable(self, index):
        
        if index.isValid():
        
            # Get zone variables
            zone_name = self.dataTable.cellWidget(index.row(),1).currentText()
            if zone_name in self._building.zones:
                zone = self._building.get_zone(zone_name)
            else:
                # If selected Zone is Environment
                zone = self._building.get_environment()
            var_list = zone.variables
            
            # Assign new variables to the combobox
            var_combo = self.dataTable.cellWidget(index.row(),2)
            var_combo.clear()
            for var in var_list:
                var_combo.addItem(var)

            # Update plot
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

            # Get selected period from GUI
            if self.predefinedPeriodCheckBox.isChecked():
                # Predefined periods
                period = SEASONS[
                    self.predefinedPeriodComboBox.currentIndex()][1]
            else :
                # Custom dates
                period = [self.beginDateEdit.date().toString('MM/dd'),
                          self.endDateEdit.date().toString('MM/dd')]
            
            # Make TimeInterval from period 
            t_interval = TimeInterval.from_string_seq(period)
            
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

