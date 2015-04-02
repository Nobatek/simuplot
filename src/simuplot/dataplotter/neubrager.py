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




class NEUBrager(DataPlotter):

    def __init__(self, building, color_chart):
        
        super(NEUBrager, self).__init__(building, color_chart)
        
        # Plot name
        self._name = self.tr("Brager comfort")
        
        # Chart and table widgets
        self._MplWidget = self.plotW
        self._table_widget = self.listW

        # Set column number and add headers
        self._table_widget.setColumnCount(4)
        self._table_widget.setHorizontalHeaderLabels([
            self.tr('Category'),
            self.tr('Below [%]'),
            self.tr('In Zone [%]'),
            self.tr('Over [%]')
            ])
        self._table_widget.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)

        # Set row number and category names
        self._table_widget.setRowCount(3)
        self._table_widget.setItem(0,0, QtGui.QTableWidgetItem("I"))
        self._table_widget.setItem(1,0, QtGui.QTableWidgetItem("II"))
        self._table_widget.setItem(2,0, QtGui.QTableWidgetItem("II"))
        
        # Refresh plot when BuildcomboBox is modified
        self.ComboZone.activated.connect(
            self.refresh_plot)        
        
    @property
    def name(self):
        return self._name

    def ComputeScatter(self, cur_zone, summer_period):
        """return Tmean Top coordinate and category colours
           for every hour for the current zone
        
        3 lists are returned :
        teta_mean coordinates [16, 20, ..., 25 ]
        teta_op coordinates [18, 219, ..., 28 ]

        """
        
        
        
        
        
    @QtCore.pyqtSlot()
    def refresh_data(self):
        # Get Building zone list (for combobox)
        zone_list = self._building.zones
        zone_list.sort()
        
        # Set combobox with zone names 
        self.ComboZone.addItems(zone_list)
        
        # Execute Refresh Plot
        self.refresh_plot()
        
    def refresh_plot(self):
        # Get end_date and begin_date from the interface calendar
        begin_date = self.BeginDate.date()
        end_date = self.EndDate.date()
        summer_period = TimeInterval([begin_date, end_date])
    
        # Get zone to plot
        cur_zone = self.BuildcomboBox.currentText()
        
        # Check if fans are activated
        if self.CheckFan.isChecked():
            air_speed = self.AirSpeedBox.value()
        else:
            air_speed = None
            
        # Compute scatter point coordinates
        teta_mean, teta_op, color = ComputeScatter(cur_zone,
                                                    summer_period,
                                                    air_speed)
            
        
    
    
    
    
    
        
            
        