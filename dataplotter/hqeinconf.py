# -*- coding: utf-8 -*-
from __future__ import division

import os

from PyQt4 import QtCore, QtGui, uic

from numpy import array

from numpy import arange,append,ones

from dataplotter import DataPlotter, DataPlotterError

from data import DataZoneError

import warnings

class HqeInconf(DataPlotter):

    @staticmethod
    def ComputeHqeInconf(zone):
    
        #configure warning for zero division
        warnings.filterwarnings('error')
        
        try:
            # Get variable OPERATIVE_TEMPERATURE in zone
            # Get PEOPLE_COUNT to determine zone occupation statut
            op_temps = zone.get_variable('OPERATIVE_TEMPERATURE', 'HOUR')
            nb_people=zone.get_variable('PEOPLE_COUNT','HOUR')
            
        except DataZoneError:
            # TODO: log warning
            return 0
        else:
            
            # creating a 0/1 presence scenario from nb_people
            io_people=array([1 if i>0 else 0
                             for i in nb_people])
                             
            # creating array of temperatures during occupation
            occ_temp=io_people*op_temps
            
            # determine maximum temperature during occupation
            max_temp=max(occ_temp)
            
            # computing % of time when temperature is above 28°C
            # according to HQE referential
            try:
                pct_hqe=(sum(array([1 if i>28 else 0 for i in occ_temp]))
                        /sum(io_people))*100
                        
            except Warning:
                pct_hqe=0
                     
            # Return % and maximum temperature in occupation [°C]
            return round(float(pct_hqe),2),round(float(max_temp),1)

    def __init__(self, building, color_chart):
        
        super(HqeInconf, self).__init__(building, color_chart)

        self._name = "Summer thermal comfort per zone"
        
        # Setup UI
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'hqeinconf.ui'),
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
            pct_hqe, max_temp = self.ComputeHqeInconf(zones[name])

            # First column: zone name + checkbox
            name_item = QtGui.QTableWidgetItem(name)

            name_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                               QtCore.Qt.ItemIsEnabled)
                               
            name_item.setCheckState(QtCore.Qt.Checked)

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
        
        ph1c=1.5
        tph1c=3

        
        # Get checked rows and corresponding (name, value)
        for i in range(self._table_widget.rowCount()):
            if self._table_widget.item(i,0).checkState() == QtCore.Qt.Checked:
                name = self._table_widget.item(i,0).text()
                names.append(name)
                try:
                    value = float(self._table_widget.item(i,1).text())
                    tmax = float(self._table_widget.item(i,2).text())
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
        ind=arange(len(values))
        rectangle=self._MplWidget.canvas.axes.bar(ind,values,edgecolor='white')
        
        # Create rectangle color map
        rect_colors = ['#E36C09' if i > tph1c
                       else
                       '#7F7F7F' if i > ph1c and i <= tph1c 
                       else
                       '#1F497D'
                       for i in values]

        #Set rectangle color
        for rec, val in zip(rectangle, rect_colors) :
            rec.set_color(val)
            
        #Adding values on top of rectangles
        for rect in rectangle:
            height = rect.get_height()
            self._MplWidget.canvas.axes.text(rect.get_x()+rect.get_width()/2.,
                                             1.0 * height,
                                             '%.1f' % round(height,1),
                                             size = 'smaller',
                                             style = 'italic',
                                             ha='center',
                                             va='bottom')
                                             
        # add some text for labels, title and axes ticks
        self._MplWidget.canvas.axes.set_ylabel('% time beyound 28C')
        self._MplWidget.canvas.axes.set_xticks(ind+rectangle[0].get_width()/2)
        self._MplWidget.canvas.axes.set_xticklabels( names, ind, ha='right',rotation=75)
        
        #plot 'Tres performant' and 'Performant' values
        #ind2 create the x vector
        ind2 = append(ind,len(values)+1)
        
        #dr_* create the y vector
        dr_ph1c = ones(len(ind2)) * ph1c
        dr_tph1c = ones(len(ind2)) * tph1c
        
        #plot lines
        self._MplWidget.canvas.axes.plot(ind2,dr_tph1c,'--',color='#1F497D',linewidth=2,)
        self._MplWidget.canvas.axes.plot(ind2,dr_ph1c,'--',color='#A5A5A5',linewidth=2,)
        
        #add annotation
        self._MplWidget.canvas.axes.annotate('%f.1 Tres Performant',
                                             xy=(5,5),
                                             ha='right')

        
        self._MplWidget.canvas.draw()
        
        
        
        
        
