# -*- coding: utf-8 -*-
from __future__ import division

import os

from PyQt4 import QtCore, QtGui, uic

import numpy as np

import matplotlib.pyplot as plt

from dataplotter import DataPlotter, DataPlotterError

from data import DataZoneError

# TODO: This module is broken if start date is not January 1st
# The simulation length must be one year, and the period 'HOUR'
# Should this be made more generic ?
periods = {'Annual' : [[0,8760]],
           'Summer' : [[2879,6553]],
           'Winter' : [[0,2779],[6553,8760]],
           }

# TODO: put this stuff somewhere else
heat_sources = ['HEATING_RATE',
                'PEOPLE_HEATING',
                'LIGHT_HEATING',
                'WINDOWS_HEATING',
                'OPAQUE_SURFACE_HEATING',
                'INFILTRATION_HEATING',
                'VENTILATION_HEATING',
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
            # If heat source not available, "mark it zero, Donnie"
            if hs in zone.variables:
                full_year_vals.append(zone.get_values(hs, 'HOUR'))
            else:
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

        self._name = "Heat gain sources"
        
        # Results dict
        self._heat_build_zone = None
        
        # Setup UI
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'heatgainpie.ui'),
            self)

        # Chart widget
        self._MplWidget = self.plotW
        
        # Table widget
        self._table_widget = self.listW

        # Set column number and add headers
        self._table_widget.setColumnCount(2)
        self._table_widget.setHorizontalHeaderLabels(['Heat sources', 
                                                      'Heat gains [kWh]'])
        self._table_widget.horizontalHeader().setResizeMode( \
            QtGui.QHeaderView.ResizeToContents)
        
        # Initialize table with one row per heat source
        self._table_widget.setRowCount(len(heat_sources))
        for i, val in enumerate(heat_sources) :
            name_item = QtGui.QTableWidgetItem(val)
            self._table_widget.setItem(i, 0, name_item)
            
        # Set PeriodcomboBox
        for dat in periods:
            self.PeriodcomboBox.addItem(dat)
        
        # Refresh plot when BuildcomboBox is modified
        self.BuildcomboBox.activated.connect( \
            self.refresh_plot)
            
        # Refresh data when PeriodcomboBox is activated
        self.PeriodcomboBox.activated.connect( \
            self.refresh_data)        

    @property
    def name(self):
        return self._name

    @QtCore.pyqtSlot()
    def refresh_data(self):
            
        # Get zones in building, sorted by name
        zones = self._building.zones
        zones.sort()
        
        # Set combobox with zone names 
        # add 'Building' as a ficticious "all zones" zone
        self.BuildcomboBox.addItems(zones)
        self.BuildcomboBox.addItem('Building')
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
       # Compute heat gain per source for building
        # by summing all zones
        self._heat_build_zone['Building'] = {}
        for hs in heat_sources:
            self._heat_build_zone['Building'][hs] = \
                sum([self._heat_build_zone[zone][hs] for zone in zones])
        
        # Draw plot
        self.refresh_plot()

    @QtCore.pyqtSlot()
    def refresh_plot(self):

        values = []
        names = []
        
        canvas = self._MplWidget.canvas
        
        # Clear axes
        canvas.axes.cla()
        
        # Current zone or building displayed
        cur_zone = str(self.BuildcomboBox.currentText())

        # Display Zone or building value in table 2nd column
        for i, hs in enumerate(heat_sources):
        
            # Get current heat gains for heat source in the zone
            hs_value = int(self._heat_build_zone[cur_zone][hs])
            
            # Set item value for column
            val_item = QtGui.QTableWidgetItem()
            val_item.setData(QtCore.Qt.DisplayRole, hs_value)
            val_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self._table_widget.setItem(i, 1, val_item)
        
            # Store name and value in lists for the plot
            names.append(hs)
            values.append(hs_value)
        
        # Create color map
        cm_array = 0.25*(np.array(values)/max(values))
        colors = plt.cm.hot(np.array(cm_array))
    
        # Create pie chart
        # (Make zone heat need non dimensional to avoid pie expansion)
        canvas.axes.pie(np.array(values) / sum(values),
                        labels=names,
                        colors=colors, autopct='%1.1f%%', 
                        shadow=False, startangle=90,)
        canvas.axes.axis('equal')        

        # Set title
        title_str = 'Building heat gains repartition'
        title = canvas.axes.set_title(title_str, y = 1.05)
        
        # Draw plot
        canvas.draw()

