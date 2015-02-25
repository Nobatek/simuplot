# -*- coding: utf-8 -*-
from __future__ import division

import os

from PyQt4 import QtCore, QtGui, uic

from numpy import array

from dataplotter import DataPlotter, DataPlotterError

from data import DataZoneError

periods = {'summer' : [[2879,6553]],
           'winter' : [[0,2779],[6553,8760]],
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
    def ComputeZoneCons(zone):
        #Initialize full_year list containing all values
        total_gain = []
        
        try:
            # Get all heat gain variable and store them in an array
            full_year = array([zone.get_variable(val, 'HOUR')
                               for val in heat_sources])

            # compute sum for each variable during the period
            for inter in periods[str(self.PeriodcomboBox.currentText())] :
                inter_val = full_year[:,inter[0]:inter[1]]
                total_gain.append(inter_val)
            
            total_gain=array(total_gain).sum(axis=0)
          
        except DataZoneError:
            # TODO: log warning
            return array([0 for i in total_gain])
        else:
            # Return the array of values in [kWh] and corresponding names
            return total_gain/1000, names
        
    def __init__(self, building, color_chart):
        
        super(HeatGainPie, self).__init__(building, color_chart)

        self._name = "Heat gain sources"
        
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
            
        # First column: zone name + checkbox
        for i, val in enumerate(heat_sources) :
            name_item = QtGui.QTableWidgetItem(val)
            self._table_widget.setItem(i, 0, name_item)
            
        # Set PeriodcomboBox
        for dat in periods:
            self.PeriodcomboBox.addItem(dat)
 
        # Refresh plot when zone is clicked/unclicked or sort order changed
        self._table_widget.itemClicked.connect(self.refresh_plot)
        self._table_widget.horizontalHeader().sectionClicked.connect( \
            self.refresh_plot)

    @property
    def name(self):
        return self._name

    @QtCore.pyqtSlot()
    def refresh_data(self):
            
        # Get zones in building
        zones = self._building.zones
        
        # Clear table
        self._table_widget.clearContents()
        
        # For each zone
        for i, name in enumerate(zones):

            # Compute total heat need
            # TODO: int or float ? explicit rounding ?
            cons = int(self.ComputeZoneCons(zones[name]))

            # By default, display zone on chart only if value not 0
            if cons != 0:
                name_item.setCheckState(QtCore.Qt.Checked)
            else:
                name_item.setCheckState(QtCore.Qt.Unchecked)

            # Second column: heat need value
            val_item = QtGui.QTableWidgetItem()
            val_item.setData(QtCore.Qt.DisplayRole, cons)
            
            val_item.setFlags(QtCore.Qt.ItemIsEnabled)

            # Add items to row, column
            self._table_widget.setItem(i, 1, val_item)
            
            #print 'NAME:', name
            #print 'name_item text()', name_item.text()
            #print 'table 0 :',self._table_widget.item(i,0).text()
            #print '\n'
        # Sort by value, descending order, and allow user column sorting
        self._table_widget.sortItems(1, QtCore.Qt.DescendingOrder)
        self._table_widget.setSortingEnabled(True)        

        # Get Building total Heat need :
        for i in range(self._table_widget.rowCount()):
            self._build_total_hn += int(self._table_widget.item(i,1).text())
        
        # Draw plot
        self.refresh_plot()

    @QtCore.pyqtSlot()
    def refresh_plot(self):

        values = []
        names = []
        building_total_hn = 0
        
        # Get checked rows and corresponding (name, value)
        for i in range(self._table_widget.rowCount()):
            if self._table_widget.item(i,0).checkState() == QtCore.Qt.Checked:
                name = self._table_widget.item(i,0).text()
                names.append(name)
                try:
                    value = int(self._table_widget.item(i,1).text())
                except AttributeError:
                    raise DataPlotterError( \
                        'Invalid cons value type for row %s (%s): %s' %
                        (i, name, self._table_widget.item(i,1)))
                except ValueError:
                    raise DataPlotterError( \
                        'Invalid cons value for row %s (%s): %s' % 
                        (i, name, self._table_widget.item(i,1).text()))
                else:
                    values.append(value)
            
        # Make zone heat need non dimensional
        values = array(values) / self._build_total_hn

        # Clear axes
        self._MplWidget.canvas.axes.cla()
    
        # Create pie chart
        self._MplWidget.canvas.axes.pie(values, labels=names, 
            colors=self._color_chart, autopct='%1.1f%%', 
            shadow=False, startangle=90)
        self._MplWidget.canvas.axes.axis('equal')
        
        #setting a title
        title_str = 'Building heat need : %d [kWh]' % self._build_total_hn
        title = self._MplWidget.canvas.axes.set_title(title_str, y = 1.05)
        
        # Draw plot
        self._MplWidget.canvas.draw()

