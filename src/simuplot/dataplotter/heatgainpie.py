# -*- coding: utf-8 -*-
from __future__ import division

from PyQt4 import QtCore, QtGui

import numpy as np

import matplotlib.pyplot as plt

from .dataplotter import DataPlotter

from simuplot.data import DataZoneError

# TODO: This module is broken if start date is not January 1st
# The simulation length must be one year, and the period 'HOUR'
# Should this be made more generic ?
periods = {'Annual' : [[0,8760]],
           'Summer' : [[2879,6553]],
           'Winter' : [[0,2779],[6553,8760]],
           }

# TODO: put this stuff somewhere else
heat_sources = ['HEATING_RATE',
                'PEOPLE_HEATING_RATE',
                'LIGHTING_HEATING_RATE',
                'EQUIPMENT_HEATING_RATE',
                'WINDOWS_HEATING_RATE',
                'OPAQUE_SURFACE_HEATING_RATE',
                'INFILTRATION_HEATING_RATE',
                ]            

class HeatGainPie(DataPlotter):

    @staticmethod
    def ComputeHeatGains(zone, study_period):
        """Return heat gain for each source for the study period
        
        Data is returned as a dict:

        {'HEATING_RATE':value,
         'PEOPLE_HEATING':value,
         ...
        }
        """
        
        # Initialize full_year_vals list containing all values for each source
        full_year_vals = []
        for hs in heat_sources:
            # If hourly heat source data not available, "mark it zero, Donnie"
            try:
                full_year_vals.append(zone.get_values(hs, 'HOUR'))
            except DataZoneError:
                full_year_vals.append(np.zeros(8760))

        # Store values as 2D numpy array
        full_year = np.array(full_year_vals)

        # Compute total gain [kWH] for each heat source
        # summing all intervals of the period
        # (Thanks to 2D array, all sources are processed at once)
        gain_per_source = np.zeros(len(heat_sources))
        for inter in periods[study_period]:
            # Extract values for interval
            inter_val = full_year[:,inter[0]:inter[1]]
            # Sum gain for interval and add it to total
            gain_per_source += inter_val.sum(axis=1)
        
        # Return results as a dictionary, with energy in [kWh]
        return dict(zip(heat_sources, gain_per_source / 1000))

    def __init__(self, building, color_chart):
        
        super(HeatGainPie, self).__init__(building, color_chart)

        self._name = self.tr("Heat gain sources")
        
        # Results dict
        self._heat_build_zone = None

        # Chart and table widgets
        self._MplWidget = self.plotW
        self._table_widget = self.listW

        # Set column number and add headers
        self._table_widget.setColumnCount(2)
        self._table_widget.setHorizontalHeaderLabels([self.tr('Heat sources'), 
                                                      self.tr('Heat gains [kWh]')])
        self._table_widget.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)
            
        # Initialize table with one row per heat source with checkbox
        self._table_widget.setRowCount(len(heat_sources))
        for i, val in enumerate(heat_sources) :
            name_item = QtGui.QTableWidgetItem(val)
            name_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                           QtCore.Qt.ItemIsEnabled)
            name_item.setCheckState(QtCore.Qt.Checked)
            
            self._table_widget.setItem(i, 0, name_item)
            
        # Set PeriodcomboBox
        for dat in periods:
            self.PeriodcomboBox.addItem(dat)
            
        # Refresh data when PeriodcomboBox is activated
        self.PeriodcomboBox.activated.connect(
            self.refresh_data)
            
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
        
        # Get the study period from combobox
        study_period = str(self.PeriodcomboBox.currentText())

        # Compute heat gain per source in each zone
        self._heat_build_zone = {}
        for name in zones :
            # Compute heat gains for desired study period
            self._heat_build_zone[name] = \
                self.ComputeHeatGains(self._building.get_zone(name),
                                      study_period)

        # Compute heat gain per source for building by summing all zones
        self._heat_build_zone['Building'] = {}
        for hs in heat_sources:
            self._heat_build_zone['Building'][hs] = \
                sum([self._heat_build_zone[zone][hs] for zone in zones])
        
        # Write in Table and draw plot
        self.refresh_tab_and_plot()

    @QtCore.pyqtSlot()
    def refresh_tab_and_plot(self):    

        # Current zone or building displayed
        if self.BuildcomboBox.currentIndex() == self.BuildcomboBox.count() - 1:
            cur_zone = 'Building'
        else :
            cur_zone = self.BuildcomboBox.currentText()

        # Display Zone or building value in table 2nd column
        for i, hs in enumerate(heat_sources):
        
            # Get current heat gains for heat source in the zone
            hs_value = int(self._heat_build_zone[cur_zone][hs])
            
            # Set item value for 2nd column
            val_item = QtGui.QTableWidgetItem()
            val_item.setData(QtCore.Qt.DisplayRole, hs_value)
            val_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self._table_widget.setItem(i, 1, val_item)
            
            # Uncheck heat source name if value is zero
            name_item = self._table_widget.item(i,0)
            if hs_value == 0:
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
        
        # Compute heat source sum and 
        # create plot list removing unchecked values
        name_plot = []
        value_plot = []
        sum_value = 0
        for i in range(self._table_widget.rowCount()):
            name = self._table_widget.item(i,0).text()
            value = int(self._table_widget.item(i,1).text())
            sum_value += value
            if self._table_widget.item(i,0).checkState() == QtCore.Qt.Checked:
                name_plot.append(name)
                value_plot.append(value)

        # If sum is 0, heat gain are 0. Do not plot anything.
        if sum_value != 0:

            # Create pie chart
            # (Make zone heat need non dimensional to avoid pie expansion)
            canvas.axes.pie(np.array(value_plot) / sum_value,
                            labels=name_plot,
                            colors=self._color_chart, autopct='%1.1f%%',
                            shadow=False, startangle=90,)
            canvas.axes.axis('equal')

            # Set title
            title_str = self.tr('Building heat gains repartition')
            title = canvas.axes.set_title(title_str, y = 1.05)
        
        # Draw plot
        canvas.draw()

