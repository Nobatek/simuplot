# -*- coding: utf-8 -*-
from __future__ import division

import os

from PyQt4 import QtCore, QtGui, uic

import numpy as np

from dataplotter import DataPlotter, DataPlotterError

from data import DataZoneError

rt_climatic_zone = {'H1a - H1b - H2a - H2b':[2,1],
                    'H1c - H2c':[2.5,1.5],
                    'H2d - H3':[3,2],
                    }
                    
hqe_tmax_per_usage = {
    u'Bureau - Enseignement':28,
    u'Hôtel':26,
    u'Commun - Circulation commerce et baignade':30,
    u'Entrepôts':35,
    }


class ThermalComfHistog(DataPlotter):

    @staticmethod
    def ComputeThermalComf(zone, ref_temp):
    
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
            
            # Computing % of time when temperature is above reference temp
            # according to HQE referential
            pct_hqe = 100 * np.count_nonzero(occ_temp > ref_temp) / nb_h_occup
                     
            # Return % and maximum temperature in occupation [°C]
            return round(float(pct_hqe),2), \
                   round(float(max_temp),1)

    def __init__(self, building, color_chart):
        
        super(ThermalComfHistog, self).__init__(building, color_chart)

        self._name = "Summer thermal comfort per zone"
        
        # Reference temperature
        self._ref_temp = None

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
                                                      'Discomfort[%]',
                                                      u'Max temp [°C]'])
        self._table_widget.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)
        
        # Initialise RTclimat_comboBox
        for dat in rt_climatic_zone:
            self.RTclimat_comboBox.addItem(dat)
            
        # Initialise HQEspace_comboBox
        for dat in hqe_tmax_per_usage :
            self.HQEspace_comboBox.addItem(dat)
            
        # Initialise HQE radio button to checked
        self.HQEradioButton.setChecked(True)
        
        # Refresh plot when zone is clicked/unclicked or sort order changed
        self._table_widget.itemClicked.connect(self.refresh_plot)
        self._table_widget.horizontalHeader().sectionClicked.connect(
            self.refresh_plot)
            
        # Refresh plot when rt_climatic_zone is changed
        self.RTclimat_comboBox.activated.connect(
            self.refresh_plot)
            
        # Refresh data when one of the two radio button is switched on or off
        self.HQEradioButton.toggled.connect(
            self.refresh_data)
        
        # Refresh data when HQEspace_comboBox is changed
        self.HQEspace_comboBox.activated.connect(
            self.refresh_data)
                
        # Refresh plot when spinBox value is changed
        self.spinBox.valueChanged.connect(
            self.refresh_data)     
     
    @property
    def name(self):
        return self._name

    @QtCore.pyqtSlot()
    def refresh_data(self):
        
        # Get zones in building
        zones = self._building.zones

        # Clear table and disable sorting before populating the table
        self._table_widget.clearContents()
        self._table_widget.setSortingEnabled(False)

        # Create one empty row per zone
        self._table_widget.setRowCount(len(zones))
        
        # Get reference temperature for thermal comfort
        if self.HQEradioButton.isChecked():
            self._ref_temp = \
                hqe_tmax_per_usage[str(self.HQEspace_comboBox.currentText())]
        else:
            self._ref_temp = self.spinBox.value()

        # For each zone
        for i, name in enumerate(zones):

            # Compute all comfort and max temperature
            pct_hqe, max_temp = self.ComputeThermalComf(zones[name], 
                                                        self._ref_temp)

            # First column: zone name + checkbox
            name_item = QtGui.QTableWidgetItem(name)
            # If comfort values known, make zone checkable and check it
            if pct_hqe != None:
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

        vals = []
        names = []
        
        # Clear axes
        self._MplWidget.canvas.axes.cla()

        # Get checked rows and corresponding (name, value)
        for i in range(self._table_widget.rowCount()):
            if self._table_widget.item(i,0).checkState() == QtCore.Qt.Checked:
                name = self._table_widget.item(i,0).text()
                names.append(name)
                try:
                    value = float(self._table_widget.item(i,1).text())
                except AttributeError:
                    raise DataPlotterError(
                        'Invalid discomfort value type for row %s (%s): %s' %
                        (i, name, self._table_widget.item(i,1)))
                except ValueError:
                    raise DataPlotterError(
                        'Invalid discomfort value for row %s (%s): %s' % 
                        (i, name, self._table_widget.item(i,1).text()))
                else:
                    vals.append(value)
        
        # If no data in vals, no zone was checked. Do not plot anything.
        if vals == []:
            return

        # Store values as np array
        values = np.array(vals)

        # TODO: shall we display HQE levels if not in HQE mode ?

        # Get "Performant" and "Très Performant" levels
        self._hqep = rt_climatic_zone[str(self.RTclimat_comboBox.currentText())][0]
        self._hqetp = rt_climatic_zone[str(self.RTclimat_comboBox.currentText())][1]
        
        # Create and draw bar chart    
        ind = np.arange(values.size)
        rectangle = self._MplWidget.canvas.axes.bar(ind, values,
                                                    edgecolor='white')
        
        # Create rectangle color map
        rect_colors = np.where(values < self._hqetp, '#1F497D', '#7F7F7F')
        rect_colors[values > self._hqep] = '#E36C09'

        # Set rectangle color
        for rec, val in zip(rectangle, rect_colors):
            rec.set_color(val)
            
        # Adding values on top of rectangles
        for rect in rectangle:
            height = rect.get_height()
            self._MplWidget.canvas.axes.text(rect.get_x()+rect.get_width()/2.,
                                             1.0 * height,
                                             '%.1f' % round(height,1),
                                             size = 'smaller',
                                             style = 'italic',
                                             ha='center',
                                             va='bottom')
                                             
        # Add text for labels, title and axes ticks
        self._MplWidget.canvas.axes.set_ylabel(
            u'%% time beyond %s°C' % self._ref_temp)
        self._MplWidget.canvas.axes.set_xticks(ind + rectangle[0].get_width()/2)
        self._MplWidget.canvas.axes.set_xticklabels(names, ind, 
                                                    ha='right', rotation=75)
        
        # Plot "Très performant" and "Performant" values
        # Create x vector ind2 and y vectors dr_*
        ind2 = np.append(ind, values.size)
        dr_hqep = np.ones(len(ind2)) * self._hqep
        dr_hqetp = np.ones(len(ind2)) * self._hqetp
        # Plot lines
        self._MplWidget.canvas.axes.plot(ind2,
                                         dr_hqetp,
                                         '--',
                                         color = '#1F497D',
                                         linewidth = 2,
                                         label = '%.1f%% TP level' %self._hqetp)
        self._MplWidget.canvas.axes.plot(ind2,
                                         dr_hqep,
                                         '--',
                                         color = '#A5A5A5',
                                         linewidth = 2,
                                         label = '%.1f%% P level' %self._hqep)
        
        # Add legend
        l = self._MplWidget.canvas.axes.legend()
        
        # Modify texts colors and style
        l.texts[0].set_color('#1F497D')
        l.texts[1].set_color('#A5A5A5')
        l.texts[0].set_style('italic')
        
        # Set title
        title = self._MplWidget.canvas.axes.set_title('Summer thermal comfort')

        self._MplWidget.canvas.draw()

