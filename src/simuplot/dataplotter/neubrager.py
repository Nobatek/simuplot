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

from copy import deepcopy




class lin_funct(object) :
    """ define a linear function from its coefficient and
        give a result for a * x + b
        a and b must be floats object
        x is can be an int, a float, a list, or an np.array
        as itss automatically convert in the compute method
    """   
    def __init__(self, a, b) :
        self._a = a
        self._b = b
        
    @property    
    def b(self) :
        return self._b
    
    @property
    def a(self) :
        return self._a
    
    def set_a(self,a) :
        self._a = a
     
    def set_b(self,b) :
        self._b = b

    def compute(self, x) :
        if x.__class__.__name__ == "int" or \
           x.__class__.__name__ == "float" or \
           x.__class__.__name__ == "float64" :
            x = np.array([x])

        elif x.__class__.__name__ == "list" :
            x = np.array(x)

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

        # Refresh data when Occupation checkbox is modified
        self.OccCheckBox.stateChanged.connect(self.create_scatter)
        
        # Refresh plot when fan spinbox is modified
        self.AirSpeedBox.valueChanged.connect(self.refresh_plot)
        
        # Refresh plot when fans are activated/deactivated
        self.CheckFan.stateChanged.connect(self.refresh_plot)
        
    @property
    def name(self):
        return self._name

    def ComputeScatter(self, cur_zone, summer_period, zone_occ):
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
        
        # Check if zone occupation is activated. If yes get people count
        if zone_occ == True :
            people_count = zone.get_values('PEOPLE_COUNT','HOUR')
            people_count = people_count.get_interval(summer_period)
                        
        # Get the Operative Temperatures values for the whole summer period
        y_op_temp = op_temp.get_interval(summer_period)
        
        # Get a list of all days and hours in the summer period
        day_list =  summer_period.get_datetimelist()
        
        # if necessary Delete operative temperature and datetime
        # from their np.array
        if zone_occ == True :
            y_op_temp = [y_op_temp[i] for i in range(len(people_count))
                         if people_count[i] > 0]
            day_list = [day_list[i] for i in range(len(people_count))
                         if people_count[i] > 0]
        
        # Create a list of mean ext temp for the period
        x_mean_ext_temp = [seven_day_mean(ext_temp, dat.date())
                           for dat in day_list]
        
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
        # Convert Qdatetime object BeginDate into date object
        begin_date = self.BeginDate.date()
        year, month, day = begin_date.getDate()
        begin_date = date(year, month, day)
        
        # Convert Qdatetime object EndDate into date object
        end_date = self.EndDate.date()
        year, month, day = end_date.getDate()
        end_date = date(year, month, day)
        
        # Create the summer TimeInterval object
        summer_period = TimeInterval([begin_date, end_date])

        # Check if occupation is taken into account
        if self.OccCheckBox.checkState() == QtCore.Qt.Checked :
            zone_occ = True
        else :
            zone_occ = None
        
        # Get zone to plot
        cur_zone = self.ComboZone.currentText()
        
        # Check if fans are activated
        if self.CheckFan.isChecked():
            air_speed = self.AirSpeedBox.value()
        else:
            air_speed = None
            
        # Compute scatter point coordinates from zone and period
        self._teta_mean, self._teta_op = self.ComputeScatter(cur_zone,
                                                             summer_period,
                                                             zone_occ)
        
        # Execute refresh_plot
        self.refresh_plot()
        
    
    def refresh_plot(self):
    
        canvas = self._MplWidget.canvas
        
        # Clear axes
        canvas.axes.cla()
        canvas.set_tight_layout_on_resize(False)
        
        # Create two x vector to plot the categories lines
        x_high = [10, 30]
        x_low = [15, 30]
        
        # Assign colour for the three category and for the over temperature
        I_colour = "#8EC02F"
        II_colour = "#E47823"
        III_colour = "#6A4300"
        ot_colour = "#868786"
        
        # If fans are present in zone, get the air speed value
        # Get the categories
        used_category = deepcopy(category)
        if self.CheckFan.checkState() == QtCore.Qt.Checked :
            # Get the air speed
            a_s = self.AirSpeedBox.value()
            
            # Compute the limit temperature rise (NF EN 15251)
            # The 4th order polynome is obtained by regression from
            # a digitized plot extract from the norm
            cor = -3.1365*a_s**4 + 12.55*a_s**3 - 18.905*a_s**2 + 14.551*a_s -2.088 
            
            # Apply correction to used_category
            for cat in used_category.keys() :
                cat_b = category[cat]['h_lim'].b
                used_category[cat]['h_lim'].set_b(cat_b + cor)
            
        # Determine in which category each point falls
        # create a colour list for the scatter plot
        colours = [ot_colour 
                   if t_op > used_category['III']['h_lim'].compute(t_mean) else 
                   III_colour 
                   if t_op > used_category['II']['h_lim'].compute(t_mean) else
                   II_colour 
                   if t_op > used_category['I']['h_lim'].compute(t_mean) else
                   I_colour 
                   if t_op > used_category['I']['l_lim'].compute(t_mean) else
                   II_colour 
                   if t_op > used_category['II']['l_lim'].compute(t_mean) else
                   III_colour 
                   if t_op > used_category['III']['l_lim'].compute(t_mean) else
                   ot_colour for t_mean, t_op in zip(self._teta_mean, self._teta_op)]
        
        # Display points
        canvas.axes.scatter(self._teta_mean, self._teta_op,
                            c = colours,
                            edgecolor = colours)
        
        # Plot category upper lines
        canvas.axes.plot(x_high, used_category['I']['h_lim'].compute(x_high),
                         '--',
                         color = I_colour,
                         linewidth = 1.5)
        canvas.axes.plot(x_high, used_category['II']['h_lim'].compute(x_high),
                         '--',
                         color = II_colour,
                         linewidth = 1.5)
        canvas.axes.plot(x_high, used_category['III']['h_lim'].compute(x_high),
                         color = III_colour,
                         linewidth = 1.5)

                         
        # Plot category lower lines
        canvas.axes.plot(x_low, used_category['I']['l_lim'].compute(x_low),
                         '--',
                         color = I_colour,
                         linewidth = 1.5)
        canvas.axes.plot(x_low, used_category['II']['l_lim'].compute(x_low),
                         '--',
                         color = II_colour,
                         linewidth = 1.5)
        canvas.axes.plot(x_low, used_category['III']['l_lim'].compute(x_low),
                         color = III_colour,
                         linewidth = 1.5)  
    
        # Draw plot
        canvas.draw()    
    
    
    
        
            
        