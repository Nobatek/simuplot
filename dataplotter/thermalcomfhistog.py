# -*- coding: utf-8 -*-
from __future__ import division

import os

from PyQt4 import QtCore, QtGui, uic

import numpy as np

from dataplotter import DataPlotter, DataPlotterError

from data import DataZoneError

class ThermalComfHistog(DataPlotter):

    @staticmethod
    def ComputeThermalComf(zone):
    
        try:
            # Get variable OPERATIVE_TEMPERATURE in zone
            # Get PEOPLE_COUNT to determine zone occupation status
            op_temps = zone.get_variable('OPERATIVE_TEMPERATURE', 'HOUR')
            nb_people = zone.get_variable('PEOPLE_COUNT','HOUR')
        except DataZoneError:
            # TODO: log warning
            # Return None as thermal confort % and None as max temperature
            return None, None
        else:
            
            # Create 0/1 presence scenario from nb_people
            io_people = np.where(nb_people > 0, 1, 0)

            # If occupation is always 0 (zone always empty),
            # return None as thermal confort % and None as max temperature
            nb_h_occup = np.count_nonzero(io_people)
            if nb_h_occup == 0:
                return None, None
                             
            # Create array of temperatures during occupation
            occ_temp = io_people * op_temps
            
            # Determine maximum temperature during occupation
            max_temp = np.amax(occ_temp)
            
            # Computing % of time when temperature is above 28°C
            # according to HQE referential
            pct_hqe = 100 * np.count_nonzero(occ_temp > 28) / nb_h_occup
                     
            # Return % and maximum temperature in occupation [°C]
            return round(float(pct_hqe),2), \
                   round(float(max_temp),1)

    def __init__(self, building, color_chart):
        
        super(ThermalComfHistog, self).__init__(building, color_chart)

        self._name = "Summer thermal comfort per zone"
        
        # Setup UI
        uic.loadUi(os.path.join(os.path.dirname(__file__), 
                                'thermalcomfhistog.ui'),
            self)

        # Chart widget
        self._MplWidget = self.plotW
        # Table widget
        self._table_widget = self.listW

        # Set column number and add headers
        self._table_widget.setColumnCount(3)
        self._table_widget.setHorizontalHeaderLabels(['Zone', 
                                                      'Comfort [%]',
                                                      'Max temp [°C]'])
        
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
        
        # Create one empty row per zone
        self._table_widget.setRowCount(len(zones))
        
        # For each zone
        for i, name in enumerate(zones):

            # Compute all comfort and max temperature
            pct_hqe, max_temp = self.ComputeThermalComf(zones[name])

            # First column: zone name + checkbox
            name_item = QtGui.QTableWidgetItem(name)

            name_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                               QtCore.Qt.ItemIsEnabled)
                               
            # By default, display zone on chart only if value not 0
            if pct_hqe != None:
                name_item.setCheckState(QtCore.Qt.Checked)
            else:
                name_item.setCheckState(QtCore.Qt.Unchecked)
            
            # Second column: % thermal comfort
            val_item1 = QtGui.QTableWidgetItem()
            val_item1.setData(QtCore.Qt.DisplayRole, pct_hqe)
            
            val_item1.setFlags(QtCore.Qt.ItemIsEnabled)
            
            # Third column: zone max temperature in occupation
            val_item2 = QtGui.QTableWidgetItem()
            val_item2.setData(QtCore.Qt.DisplayRole, max_temp)
            
            val_item2.setFlags(QtCore.Qt.ItemIsEnabled)

            # Add items to row, column
            self._table_widget.setItem(i, 0, name_item)
            self._table_widget.setItem(i, 1, val_item1)
            self._table_widget.setItem(i, 2, val_item2)

        # Sort by value, descending order, and allow user column sorting
        self._table_widget.sortItems(1, QtCore.Qt.DescendingOrder)
        self._table_widget.setSortingEnabled(True)

        # Draw plot
        self.refresh_plot()

    @QtCore.pyqtSlot()
    def refresh_plot(self):

        values = []
        names = []
        
        # Get checked rows and corresponding (name, value)
        for i in range(self._table_widget.rowCount()):
            if self._table_widget.item(i,0).checkState() == QtCore.Qt.Checked:
                name = self._table_widget.item(i,0).text()
                names.append(name)
                try:
                    value = float(self._table_widget.item(i,1).text())
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
        
        # Clear axes
        self._MplWidget.canvas.axes.cla()
    
        # Create and draw bar chart    
        ind=np.arange(len(values))
        
        self._MplWidget.canvas.axes.bar(ind,values,facecolor='#FF9933',edgecolor='white')
        
        # add some text for labels, title and axes ticks
        self._MplWidget.canvas.axes.set_ylabel('% time beyond 28C')
        self._MplWidget.canvas.axes.set_xticklabels( names, ind, rotation=45)

        
        self._MplWidget.canvas.draw()
