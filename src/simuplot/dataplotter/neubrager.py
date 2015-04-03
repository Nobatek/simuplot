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


def seven_day_mean(ext_temp, cur_day) :
    """Return a single temperature corresponding to the 
    mean temperature of the last 7 days according to EU norm
    E 51-762 and french adaptation NF EN 15251
    
    The arguments of this function are an Array and a date object.
    
    """
    # Create a list of interval corresponding to the 7 last days
    seven_day_list=[[cur_day-timedelta(days = i),
                     cur_day-timedelta(days = i)]
                     for i in range(7)]
    
    # Replace the date if cur day is the first week of January
    seven_day_list = [[inter[0].replace(year = 2005),
                       inter[0].replace(year = 2005)]
                       for inter in seven_day_list]
                       
    print (seven_day_list)
    
    # Create a list of time interval objects
    seven_day_list = [TimeInterval(day) for day in seven_day_list]
    
    # Create a list of mean temperature for each days
    seven_temp = [ext_temp.mean_interval(inter)
                  for inter in seven_day_list]
    
    print (seven_temp)
    
    print (sum(seven_temp)/len(seven_temp))
    
    # Return seven_day_mean temperature
    return sum(seven_temp)/len(seven_temp)
    
             
    


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
        
        # Get the Outdoor temperature Array from the environment
        # TODO : exception if no environment 
        environment = self._building.get_environment()
        ext_temp = environment.get_values('AIR_DRYBULB_TEMPERATURE','HOUR')
        
        # Get the Operative temperature Array for the zone
        zone = self._building.get_zone(cur_zone)
        op_temp = zone.get_values('OPERATIVE_TEMPERATURE','HOUR')
        
        seven_day_mean(ext_temp, summer_period.begin_date)

        
        
        
        
    @QtCore.pyqtSlot()
    def refresh_data(self):
        # Get Building zone list (for combobox)
        zone_list = self._building.zones
        zone_list.sort()
        
        # Set combobox with zone names 
        self.ComboZone.addItems(zone_list)
        
        # Execute Refresh Plot
        self.create_scatter()
        
    def create_scatter(self):
        # Convert Qdatetime object BeinDate into date object
        begin_date = self.BeginDate.date()
        year, month, day = begin_date.getDate()
        begin_date = date(year, month, day)
        
        # Convert Qdatetime object end_date into date object
        end_date = self.EndDate.date()
        year, month, day = end_date.getDate()
        end_date = date(year, month, day)
        
        summer_period = TimeInterval([begin_date, end_date])
        
        # Get zone to plot
        cur_zone = self.ComboZone.currentText()
        
        # Check if fans are activated
        if self.CheckFan.isChecked():
            air_speed = self.AirSpeedBox.value()
        else:
            air_speed = None
            
        # Compute scatter point coordinates
        teta_mean, teta_op = self.ComputeScatter(cur_zone, summer_period)
                                                    
            
        
    
    
    
    
    
        
            
        