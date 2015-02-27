# -*- coding: utf-8 -*-
from __future__ import division

import os

from PyQt4 import QtCore, QtGui, uic

from numpy import array, zeros, concatenate

from dataplotter import DataPlotter, DataPlotterError

import matplotlib.pyplot as plt

from data import DataZoneError

periods = {'Annual' : [[0,8760]],
           'Summer' : [[2879,6553]],
           'Winter' : [[0,2779],[6553,8760]],
            }

# TODO put this stuff somewhere else
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
    def ComputeHeatGains(zone,study_period):
        #Initialize full_year list containing all values
        total_gain = []
        
        try:
            # Get all available heat gain variable names
            avail_var=zone.get_varlist()
            avail_var=[val for val in avail_var
                       if val in heat_sources]
                       
            # Get all heat gain variable available and store them in an array
            full_year = array([zone.get_variable(val, 'HOUR')
                               for val in avail_var])
                       
        except DataZoneError:
            # TODO: log warning
            return {hg : None for hg in heat_sources}
            
        else:               
            # compute sum for each variable during the period in [kWh]
            # compute the sum for each interval in period
            for inter in periods[study_period] :
                inter_val = full_year[:,inter[0]:inter[1]]
                total_gain.append(inter_val.sum(axis=1))
            
            #compute period total gain
            total_gain = array(total_gain).sum(axis=0)/1000
   
            # return a dictionary with results
            return {name : value for name, value in zip(avail_var, total_gain)}

        
          


        
    def __init__(self, building, color_chart):
        
        super(HeatGainPie, self).__init__(building, color_chart)

        self._name = "Heat gain sources"
        
        #define empty dictionary result
        self._heat_build_zone = {}
        
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
        
        # Set row number
        self._table_widget.setRowCount(len(heat_sources))
        
        # Set row names (heat sources)
        for i, val in enumerate(heat_sources) :
            name_item = QtGui.QTableWidgetItem(val)
            self._table_widget.setItem(i, 0, name_item)
            
        # Set PeriodcomboBox
        for dat in periods:
            self.PeriodcomboBox.addItem(dat)
        
        # Set combobox with Building
        #list_build_zone_init = ['Building']
        #self.BuildcomboBox.addItems(list_build_zone_init)
        
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
            
        # Get zones in building
        zones = self._building.zones
        
        # Create a list of zone name sorted by name and add 'Building'
        list_build_zone = [z for z in zones]
        list_build_zone.sort()
        list_build_zone.append('Building')

        # Set combobox with zone name and building
        self.BuildcomboBox.addItems(list_build_zone)
        #self.BuildcomboBox.setCurrentIndex(list_build_zone.index('Building'))
        
        # Create dictionary containing dictionary results for each 'zones'
        self._heat_build_zone = {z : {} for z in list_build_zone}
        
        # Get the study period from combobox
        study_period = str(self.PeriodcomboBox.currentText())
              
        # For each zone
        for name in zones :
            # Compute heat gains for desired study period
            self._heat_build_zone[name] = self.ComputeHeatGains(zones[name],study_period)
            print 'zone', name
            print self._heat_build_zone[name]
            print '\n'
            
        # Compute building results
        # For each heat sources      
        for hs in heat_sources :
            #sum all zone value if available
            hs_sum = sum([self._heat_build_zone[zone][hs] 
                          for zone in zones
                          if hs in self._heat_build_zone[zone].keys()])
            
            #add it to the Buiding dictionary in self._heat_build_zone
            self._heat_build_zone['Building'][hs] = hs_sum
        
        # Draw plot
        self.refresh_plot()

    @QtCore.pyqtSlot()
    def refresh_plot(self):

        values = []
        names = []
        
        # Current zone or building displayed
        cur_zone = str(self.BuildcomboBox.currentText())

        # Display Zone or building value in table 2nd column
        for row in range(self._table_widget.rowCount()) :
        
            # Get current heat source and corresponding value
            cur_hs = str(self._table_widget.item(row,0).text())
            if cur_hs in self._heat_build_zone[cur_zone].keys() :
                cur_hs_value = int(self._heat_build_zone[cur_zone][cur_hs])
            else :
                cur_hs_value = 0
            
            #Set item value for column
            val_item = QtGui.QTableWidgetItem()
            val_item.setData(QtCore.Qt.DisplayRole, cur_hs_value)
            val_item.setFlags(QtCore.Qt.ItemIsEnabled)
            
            self._table_widget.setItem(row, 1, val_item)
        
        # Get rows and corresponding (name, value)
        for i in range(self._table_widget.rowCount()):
            name = self._table_widget.item(i,0).text()
            names.append(name)
            try:
                value = int(self._table_widget.item(i,1).text())
            except AttributeError:
                raise DataPlotterError( \
                    'Invalid heat gain type for row %s (%s): %s' %
                    (i, name, self._table_widget.item(i,1)))
            except ValueError:
                raise DataPlotterError( \
                    'Invalid heat gain value for row %s (%s): %s' % 
                    (i, name, self._table_widget.item(i,1).text()))
            else:
                values.append(value)
        
        # Make array for colormap
        cm_array = 0.25*(array(values)/max(values))
        
        # Make zone heat gains non dimensional
        values = array(values) / sum(values)

        # Clear axes
        self._MplWidget.canvas.axes.cla()
        
        # Create color map
        cmap = plt.cm.hot
        colors = cmap(array(cm_array))
    
        # Create pie chart
        self._MplWidget.canvas.axes.pie(values, labels=names, 
            colors=colors, autopct='%1.1f%%', 
            shadow=False, startangle=90,)
        self._MplWidget.canvas.axes.axis('equal')        

        
        #setting a title
        title_str = 'Building heat gains repartition'
        title = self._MplWidget.canvas.axes.set_title(title_str, y = 1.05)
        
        # Draw plot
        self._MplWidget.canvas.draw()

