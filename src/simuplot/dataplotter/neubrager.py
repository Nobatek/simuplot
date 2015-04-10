# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QT_TRANSLATE_NOOP as translate

from copy import deepcopy
import datetime as dt
import numpy as np
import matplotlib.dates as dates

from simuplot.data import TimeInterval
from .dataplotter import DataPlotter, DataPlotterError

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
        
        # Set column number and add headers
        self.dataTable.setColumnCount(4)
        self.dataTable.setHorizontalHeaderLabels([
            self.tr('Category'),
            self.tr('Below [%]'),
            self.tr('In Zone [%]'),
            self.tr('Over [%]')
            ])
        self.dataTable.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)

        # Set row number and category names
        self.dataTable.setRowCount(3)
        self.dataTable.setItem(0,0, QtGui.QTableWidgetItem("I"))
        self.dataTable.setItem(1,0, QtGui.QTableWidgetItem("II"))
        self.dataTable.setItem(2,0, QtGui.QTableWidgetItem("II"))
        
        # Refresh plot when BuildcomboBox is modified
        self.zoneSelectBox.activated.connect(self.create_scatter)

        # Refresh data when begin date or end date is changed
        self.beginDateEdit.dateChanged.connect(self.create_scatter)
        self.endDateEdit.dateChanged.connect(self.create_scatter)

        # Refresh data when Occupation checkbox is modified
        self.occupCheckBox.stateChanged.connect(self.create_scatter)
        
        # Refresh plot when fans are modified
        self.fanAirSpeedSpinBox.valueChanged.connect(self.refresh_plot)
        self.fanCheckBox.stateChanged.connect(self.refresh_plot)
        
    @property
    def name(self):
        return self._name

    @QtCore.pyqtSlot()
    def refresh_data(self):

        # TODO: fix issues if opening a new data file
        
        # Get Building zone list (for combobox)
        zone_list = self._building.zones
        zone_list.sort()
        
        # Set combobox with zone names 
        self.zoneSelectBox.addItems(zone_list)
        
        # Execute Refresh Plot
        self.create_scatter()
        
    @QtCore.pyqtSlot()
    def create_scatter(self):
        
        # Define TimeInterval from summer period
        time_int = TimeInterval.from_string_seq(
            [self.beginDateEdit.date().toString('MM/dd'),
             self.endDateEdit.date().toString('MM/dd')])

        # Create a list of mean ext temp for the period
        # TODO: exception if no environment 
        environment = self._building.get_environment()
        t_out = environment.get_array('AIR_DRYBULB_TEMPERATURE', 'HOUR')
        t_out_mean = np.repeat(
          [t_out.mean(TimeInterval(dt_day + dt.timedelta(days=-7), dt_day))
           for dt_day in time_int.get_dt_range('DAY')], 24)
        
        # Get the Operative Temperatures values for the whole summer period
        zone = self._building.get_zone(self.zoneSelectBox.currentText())
        t_in = zone.get_array(
            'OPERATIVE_TEMPERATURE', 'HOUR').values(time_int)
        
        # If "zone occupation" is activated, 
        # only consider times when occupation is not 0
        if self.occupCheckBox.isChecked:
            occupation = np.where(zone.get_array(
                'PEOPLE_COUNT', 'HOUR').values(time_int))
            
            self._teta_mean = t_out_mean[occupation]
            self._teta_op = t_in[occupation]
        else:
            self._teta_mean = t_out_mean
            self._teta_op = t_in

        # Refresh_plot
        self.refresh_plot()
        
    def refresh_plot(self):
    
        canvas = self.plotWidget.canvas
        
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
        if self.fanCheckBox.checkState() == QtCore.Qt.Checked :
            # Get the air speed
            a_s = self.fanAirSpeedSpinBox.value()
            
            # Compute the limit temperature rise (NF EN 15251)
            # The 4th order polynom is obtained by regression from
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
                         '--', color = I_colour, linewidth = 1.5)
        canvas.axes.plot(x_high, used_category['II']['h_lim'].compute(x_high),
                         '--', color = II_colour, linewidth = 1.5)
        canvas.axes.plot(x_high, used_category['III']['h_lim'].compute(x_high),
                         color = III_colour, linewidth = 1.5)
 
        # Plot category lower lines
        canvas.axes.plot(x_low, used_category['I']['l_lim'].compute(x_low),
                         '--', color = I_colour, linewidth = 1.5)
        canvas.axes.plot(x_low, used_category['II']['l_lim'].compute(x_low),
                         '--', color = II_colour, linewidth = 1.5)
        canvas.axes.plot(x_low, used_category['III']['l_lim'].compute(x_low),
                         color = III_colour, linewidth = 1.5)  

        canvas.set_tight_layout_on_resize(True)

        # Draw plot
        canvas.draw()    

