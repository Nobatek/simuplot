# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QT_TRANSLATE_NOOP as translate

import datetime as dt
import numpy as np
import matplotlib.dates as dates

from simuplot.data import TimeInterval, DataZoneError
from .dataplotter import DataPlotter

CATEGORY_OFFSET = {'I': 2, 'II': 3, 'III': 4}

CATEGORY_COLOR = {'I': '#8EC02F',
                  'II': '#E47823',
                  'III': '#6A4300',
                  'out': '#868786'}

def comfort_temp(mean_temp):
    """Returns the comfort temperature associated to outdoor mean temperature
       
       mean_temp (scalar or array_like): outdoor mean temperature
    """
    return 0.33 * mean_temp + 18.8

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
        
        # Mean outdoor temperature and Zone operative temperature
        self._teta_mean = None
        self._teta_op = None

        # Refresh temperatures when Zone or analysis period changed
        self.zoneSelectBox.activated.connect(self.refresh_temperatures)
        self.beginDateEdit.dateChanged.connect(self.refresh_temperatures)
        self.endDateEdit.dateChanged.connect(self.refresh_temperatures)
        self.occupCheckBox.stateChanged.connect(self.refresh_temperatures)
        
        # Refresh plot when fans are modified
        self.fanAirSpeedSpinBox.valueChanged.connect(self.refresh_plot)
        self.fanCheckBox.stateChanged.connect(self.refresh_plot)
        
    @property
    def name(self):
        return self._name

    @QtCore.pyqtSlot()
    def refresh_data(self):

        # Fill Zone selection box with Zone names
        zone_list = self._building.zones
        zone_list.sort()
        self.zoneSelectBox.clear()
        self.zoneSelectBox.addItems(zone_list)
        
        # Compute temperature arrays
        self.refresh_temperatures()
        
    @QtCore.pyqtSlot()
    def refresh_temperatures(self):
        """Compute temperature arrays
        
           self._teta_mean: mean outdoor temperature
           self._teta_op: operative temperature for the Zone
        """
        
        environment = self._building.get_environment()
        
        # If no environment, or no Zone, nothing to plot
        if environment is None or self.zoneSelectBox.count() == 0:
            self._teta_mean = None
            self._teta_op = None

        else:
            
            # Instantiate TimeInterval for summer period
            time_int = TimeInterval.from_string_seq(
                [self.beginDateEdit.date().toString('MM/dd'),
                 self.endDateEdit.date().toString('MM/dd')])

            # Create a list of mean ext temp for the period
            # t_out_mean associates to each hour the averate temperature
            # of the last 7 entire days.
            # (Therefore, for a given day, all values are the same.)
            t_out = environment.get_array('AIR_DRYBULB_TEMPERATURE', 'HOUR')
            t_out_mean = np.repeat(
              [t_out.mean(TimeInterval(dt_day + dt.timedelta(days=-7), dt_day))
               for dt_day in time_int.get_dt_range('DAY')], 24)
            
            # Get the Operative Temperatures values for the whole summer period
            zone = self._building.get_zone(self.zoneSelectBox.currentText())
            try:
                t_in = zone.get_array(
                    'OPERATIVE_TEMPERATURE', 'HOUR').values(time_int)
            # If operative temperature not provided, nothing to plot
            except DataZoneError:
                self._teta_mean = None
            else:
                # If "zone occupation" is activated, 
                # only consider times when occupation is not 0
                if self.occupCheckBox.isChecked():
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
        
        # If there is data to plot
        if self._teta_op is not None:
        
            # If fans are present in zone, correct comfort temperature
            corr = 0
            if self.fanCheckBox.isChecked():
                # Get the air speed
                a_s = self.fanAirSpeedSpinBox.value()
                
                # Compute the limit temperature rise (NF EN 15251)
                # The 4th order polynom is obtained by regression from
                # a digitized plot extract from the norm
                corr = (-3.1365*a_s**4 + 12.55*a_s**3 - 
                        18.905*a_s**2 + 14.551*a_s -2.088)
                
            # Compute fan-corrected comfort temperature array
            t_comf = comfort_temp(self._teta_mean)

            # Determine in which comfort category each point falls and
            # create a colour array for the scatter plot
            colors = np.empty_like(self._teta_mean, dtype='<U7')
            colors[:] = CATEGORY_COLOR['out']
            colors[np.where(self._teta_op > t_comf -
                CATEGORY_OFFSET['III'])] = CATEGORY_COLOR['III']
            colors[np.where(self._teta_op > t_comf -
                CATEGORY_OFFSET['II'])] = CATEGORY_COLOR['II']
            colors[np.where(self._teta_op > t_comf -
                CATEGORY_OFFSET['I'])] = CATEGORY_COLOR['I']
            colors[np.where(self._teta_op >= t_comf + corr +
                CATEGORY_OFFSET['I'])] = CATEGORY_COLOR['II']
            colors[np.where(self._teta_op >= t_comf + corr +
                CATEGORY_OFFSET['II'])] = CATEGORY_COLOR['III']
            colors[np.where(self._teta_op >= t_comf + corr +
                CATEGORY_OFFSET['III'])] = CATEGORY_COLOR['out']

            # Display points
            canvas.axes.scatter(self._teta_mean, self._teta_op, color=colors)
            
            # Plot categories upper limits
            x_high = np.array([10, 30])
            t_comf_high = comfort_temp(x_high)
            canvas.axes.plot(x_high, 
                             t_comf_high + CATEGORY_OFFSET['I'] + corr,
                             '--', color = CATEGORY_COLOR['I'], 
                             linewidth = 1.5)
            canvas.axes.plot(x_high, 
                             t_comf_high + CATEGORY_OFFSET['II'] + corr,
                             '--', color = CATEGORY_COLOR['II'], 
                             linewidth = 1.5)
            canvas.axes.plot(x_high, 
                             t_comf_high + CATEGORY_OFFSET['III'] + corr,
                             color = CATEGORY_COLOR['II'],
                             linewidth = 1.5)
     
            # Plot categories lower limits
            x_low = np.array([15, 30])
            t_comf_low = comfort_temp(x_low)
            canvas.axes.plot(x_low,
                             t_comf_low - CATEGORY_OFFSET['I'],
                             '--', color = CATEGORY_COLOR['I'], 
                             linewidth = 1.5)
            canvas.axes.plot(x_low,
                             t_comf_low - CATEGORY_OFFSET['II'],
                             '--', color = CATEGORY_COLOR['II'], 
                             linewidth = 1.5)
            canvas.axes.plot(x_low,
                             t_comf_low - CATEGORY_OFFSET['III'],
                             color = CATEGORY_COLOR['III'], 
                             linewidth = 1.5)

            canvas.set_tight_layout_on_resize(True)

        # Draw plot
        canvas.draw()    

