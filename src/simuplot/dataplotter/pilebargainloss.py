# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import QT_TRANSLATE_NOOP as translate

import numpy as np

import matplotlib.pyplot as plt

from .dataplotter import DataPlotter

from simuplot.data import DataTypes, DataZoneError

from datetime import date, datetime, time, timedelta

from simuplot.data import TimeInterval

from operator import add

# TODO: put this stuff somewhere else
heat_sources = ['HEATING_RATE',
                'PEOPLE_HEATING_RATE',
                'LIGHTING_HEATING_RATE',
                'EQUIPMENT_HEATING_RATE',
                'WINDOWS_HEATING_RATE',
                'OPAQUE_SURFACES_HEATING_RATE',
                'INFILTRATION_HEATING_RATE',
                ]

# Define intervals for months in a non leap year  
year_period = {"Jan" : [datetime(2005,1,1,0,0,0),datetime(2005,1,31,23,0,0)],
               "Feb" : [datetime(2005,2,1,0,0,0),datetime(2005,2,28,23,0,0)],
               "Mar" : [datetime(2005,3,1,0,0,0),datetime(2005,3,31,23,0,0)],
               "Apr" : [datetime(2005,4,1,0,0,0),datetime(2005,4,30,23,0,0)],
               "May" : [datetime(2005,5,1,0,0,0),datetime(2005,5,31,23,0,0)],
               "Jun" : [datetime(2005,6,1,0,0,0),datetime(2005,6,30,23,0,0)],
               "Jul" : [datetime(2005,7,1,0,0,0),datetime(2005,7,31,23,0,0)],
               "Aug" : [datetime(2005,8,1,0,0,0),datetime(2005,8,31,23,0,0)],
               "Sep" : [datetime(2005,9,1,0,0,0),datetime(2005,9,30,23,0,0)],
               "Oct" : [datetime(2005,10,1,0,0,0),datetime(2005,10,31,23,0,0)],
               "Nov" : [datetime(2005,11,1,0,0,0),datetime(2005,11,30,23,0,0)],
               "Dec" : [datetime(2005,12,1,0,0,0),datetime(2005,12,31,23,0,0)]
              }

# Create a month list
month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class PileBarGainLoss(DataPlotter):

    def __init__(self, building, color_chart):
        
        super(PileBarGainLoss, self).__init__(building, color_chart)

        self._name = self.tr("Heat gains per source")
        
        # Results dict
        self._heat_build_zone = None

        # Chart and table widgets
        self._MplWidget = self.plotW
        self._table_widget = self.listW

        # Set column number and add headers
        self._table_widget.setColumnCount(13)
        self._table_widget.setHorizontalHeaderLabels(
            [self.tr('Heat sources')]+month_list)
        self._table_widget.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)
            
        # Initialize table with one row per heat source with checkbox
        self._table_widget.setRowCount(len(heat_sources))
        for i, val in enumerate(heat_sources) :
            # DataTypes is a dict of type:(unit, string)
            hs_name = QtCore.QCoreApplication.translate(
                'Data', DataTypes[val][1])
            name_item = QtGui.QTableWidgetItem(hs_name)
            name_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                           QtCore.Qt.ItemIsEnabled)
            name_item.setCheckState(QtCore.Qt.Checked)
            
            self._table_widget.setItem(i, 0, name_item)
            
        # Refresh plot when BuildcomboBox is modified
        self.BuildcomboBox.activated.connect(
            self.refresh_tab_and_plot)

        # Refresh plot when zone is clicked/unclicked or sort order changed
        self._table_widget.itemClicked.connect(self.refresh_plot)
        self._table_widget.horizontalHeader().sectionClicked.connect(
            self.refresh_plot)    
            
    @property
    def name(self):
        return self._name

    def ComputeGainLoss(self, zone):
        """Return 12 np.array representing monthly values for each sources 
        
        Data is returned as a dict:

        {'HEATING_RATE':value [12],
         'PEOPLE_HEATING':value [12],
         ...
        }
        """
        
        # Initialize full_year_vals list containing all values for each source
        full_year_vals = []
        
        for hs in heat_sources:
            hs_year_values = np.array([])
            # If hourly heat source data not available, "mark it zero, Donnie"
            try:
                # Get the Array object for current heat source
                val_array = zone.get_values(hs, 'HOUR')

                for month in month_list :
                    # Create TimeInterval for current month
                    month_timeint = TimeInterval(year_period[month])
                    # Get monthly sum
                    cur_month_val = val_array.sum_interval(month_timeint)
                    hs_year_values = np.append(hs_year_values,cur_month_val)
                    
            except DataZoneError:
                hs_year_values = np.zeros(12)

            full_year_vals.append(hs_year_values)

        # Store values as 2D numpy array
        full_year = np.array(full_year_vals)
        
        # Return results as a dictionary, with energy in [kWh]
        return dict(zip(heat_sources, full_year / 1000))

    @QtCore.pyqtSlot()
    def refresh_data(self):
            
        # Get zones in building, sorted by name
        zones = self._building.zones
        zones.sort()
        
        # Set combobox with zone names 
        # and add 'Building' as a ficticious "all zones" zone
        self.BuildcomboBox.addItems(zones)
        self.BuildcomboBox.addItem(self.tr('Building'))
        self.BuildcomboBox.setCurrentIndex(self.BuildcomboBox.count() - 1)

        # Compute heat gain per source in each zone
        self._heat_build_zone = {}
        for name in zones :
            # Compute heat gains for desired study period
            self._heat_build_zone[name] = \
                self.ComputeGainLoss(self._building.get_zone(name))

        # Compute heat gain per source for building by summing all zones
        self._heat_build_zone['Building'] = {}
        for hs in heat_sources:
            self._heat_build_zone['Building'][hs] = \
                np.sum([self._heat_build_zone[zone][hs] for zone in zones],
                       axis =0)
        
        # Write in Table and draw plot
        self.refresh_tab_and_plot()

    @QtCore.pyqtSlot()
    def refresh_tab_and_plot(self):    

        # Current zone or building displayed
        if self.BuildcomboBox.currentIndex() == self.BuildcomboBox.count() - 1:
            cur_zone = 'Building'
        else :
            cur_zone = self.BuildcomboBox.currentText()

        # Display Zone or building values in table
        for i, hs in enumerate(heat_sources):
            # Get current heat gains for heat source in the zone
            hs_value = self._heat_build_zone[cur_zone][hs]
            
            for j, monthly_val in enumerate(hs_value):
                # Set item value for month column
                val_item = QtGui.QTableWidgetItem()
                val_item.setData(QtCore.Qt.DisplayRole, int(monthly_val))
                val_item.setFlags(QtCore.Qt.ItemIsEnabled)
                self._table_widget.setItem(i, j+1, val_item)
            
            # Uncheck heat source name if value is zero
            name_item = self._table_widget.item(i,0)
            if np.sum(hs_value) == 0:
                name_item.setCheckState(QtCore.Qt.Unchecked)
            else :
                name_item.setCheckState(QtCore.Qt.Checked)      
        
        # Draw plot
        self.refresh_plot()
        
    @QtCore.pyqtSlot()
    def refresh_plot(self):
        
        canvas = self._MplWidget.canvas
        
        # Clear axes
        canvas.axes.cla()
        
        # Get all heat sources names
        hs_names = [self._table_widget.item(i,0).text()
                    for i in range(self._table_widget.rowCount())]
        
        # Compute heat source sum and 
        # create plot list removing unchecked values
        name_plot = []
        value_plot = []
        sum_value = 0
        for i in range(self._table_widget.rowCount()):
            name = self._table_widget.item(i,0).text()
            month_vals = []
            for j in range(1, self._table_widget.columnCount()):
                month_vals.append(int(self._table_widget.item(i,j).text()))
            if self._table_widget.item(i,0).checkState() == QtCore.Qt.Checked:
                name_plot.append(name)
                value_plot.append(month_vals)

        
        # Create a uniform x axis        
        ind = np.arange(len(month_list))
        
        # Create a colormap adapted to heat_sources
        hs_cmap = {hs_names[i] : self._color_chart[i] 
                   for i in range(len(heat_sources))}
        
        # Create and draw bar chart
        prev_height = []
        rectangle = []
        for i, (hs_name, hs_val) in enumerate(zip(name_plot, value_plot)):
            #initialize plot
            if i == 0 :
                rectangle = canvas.axes.bar(ind, hs_val, 
                                            edgecolor = 'white',
                                            color = hs_cmap[hs_name],
                                            label = hs_name)
                prev_height = hs_val

            # Draw rectangle on top of the previous one
            else :
                rectangle = canvas.axes.bar(ind, hs_val, 
                                            edgecolor = 'white',
                                            color = hs_cmap[hs_name],
                                            bottom = prev_height,
                                            label = hs_name)
                                            
                # Store current HS height for future iteration
                prev_height = map(add, prev_height, hs_val)
            
        # Add text for labels, title and axes ticks
        canvas.axes.set_ylabel(self.tr(
            'heat gains / loss [kWh]'))
        canvas.axes.set_xticks(ind + rectangle[0].get_width()/2)
        canvas.axes.set_xticklabels(month_list, ind, ha='center')
        
        # Set title
        title_str = self.tr('Heat gains repartition')
        title = canvas.axes.set_title(title_str, y = 1.05)
        
        # Add legend
        l = canvas.axes.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, ncol=4)

        for text in l.texts :
            text.set_size('small')
                
        
        # Draw plot
        canvas.draw()

