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




class lin_funct(object) :
    """ define a linear function from its coefficient and
        give a result for a * x + b
        a and b must be floats object
        x is an np.array
    """   
    def __init__(self, a, b) :
        self._a = a
        self._b = b
    
    def set_a(self,a) :
        self._a = a
     
    def set_b(self,b) :
        self._b = b

    def compute(self, x) :  
        b = np.ones(len(x)) * self._b
        return self._a * x + self._b
    


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
    
    # Create a list of time interval objects
    seven_day_list = [TimeInterval(day) for day in seven_day_list]
    
    # Create a list of mean temperature for each days
    seven_temp = [ext_temp.mean_interval(inter)
                  for inter in seven_day_list]
    
    # Return seven_day_mean temperature
    return sum(seven_temp)/len(seven_temp)
    
             
    
# Category definition from NF EN 15251
category = {'I' : {'h_lim' : lin_funct(0.33, 18.8 + 2),
                   'l_lim' : lin_funct(0.33, 18.8 - 2)},
            'II' : {'h_lim' : lin_funct(0.33, 18.8 + 3),
                    'l_lim' : lin_funct(0.33, 18.8 - 3)},
            'III' : {'h_lim' : lin_funct(0.33, 18.8 + 4),
                     'l_lim' : lin_funct(0.33, 18.8 - 4)}
            }


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
            self.create_scatter)

        # Refresh data when begin date or end date is changed
        self.BeginDate.dateChanged.connect(self.create_scatter)
        self.EndDate.dateChanged.connect(self.create_scatter)            
        
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
        
        # Get the Operative Temperatures values for the period
        y_op_temp = op_temp.get_interval(summer_period)
        # print (y_op_temp)
        
        # Get a list of all days and hours in the summer period
        day_list =  summer_period.get_datetimelist()
        
        # Create a list of mean ext temp for the period
        x_mean_ext_temp = [seven_day_mean(ext_temp, dat.date())
                           for dat in day_list]
        # print (x_mean_ext_temp)
        
        return x_mean_ext_temp, y_op_temp
        

        
        
        
        
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
            
        # Compute scatter point coordinates from zone and period
        self._teta_mean, self._teta_op = self.ComputeScatter(cur_zone, summer_period)
        
        # Execute refresh_plot
        self.refresh_plot()
        
    
    def refresh_plot(self):
    
        canvas = self._MplWidget.canvas
        
        # Clear axes
        canvas.axes.cla()
        canvas.set_tight_layout_on_resize(False)
        
        # Display points
        canvas.axes.scatter(self._teta_mean, self._teta_op)
        
        # Create two x vector to plot the categories lines
        x_high = np.array([10, 30])
        x_low = np.array([15, 30])
        
        # Plot category upper lines
        canvas.axes.plot(x_high, category['I']['h_lim'].compute(x_high),
                         '--',
                         color = "#8EC02F",
                         linewidth = 1.5)
        canvas.axes.plot(x_high, category['II']['h_lim'].compute(x_high),
                         '--',
                         color = "#E47823",
                         linewidth = 1.5)
        canvas.axes.plot(x_high, category['III']['h_lim'].compute(x_high),
                         color = "r",
                         linewidth = 1.5)

                         
        # Plot category lower lines
        canvas.axes.plot(x_low, category['I']['l_lim'].compute(x_low),
                         '--',
                         color = "#8EC02F",
                         linewidth = 1.5)
        canvas.axes.plot(x_low, category['II']['l_lim'].compute(x_low),
                         '--',
                         color = "#E47823",
                         linewidth = 1.5)
        canvas.axes.plot(x_low, category['III']['l_lim'].compute(x_low),
                         color = "r",
                         linewidth = 1.5)  
    
        # Draw plot
        canvas.draw()    
    
    
    
        
            
        