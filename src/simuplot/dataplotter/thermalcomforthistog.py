# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from PyQt4 import QtCore, QtGui

import numpy as np

from .dataplotter import DataPlotter, DataPlotterError

from simuplot.data import DataZoneError

RT_CLIMATIC_ZONE = {'H1a - H1b - H2a - H2b': [2, 1],
                    'H1c - H2c': [2.5, 1.5],
                    'H2d - H3': [3, 2],
                   }

HQE_TMAX_PER_USAGE = {
    'Bureau - Enseignement': 28,
    'Hôtel': 26,
    'Commun - Circulation commerce et baignade': 30,
    'Entrepôts': 35,
    }

def eval_thermal_comfort(zone, ref_temp):
    """Evaluate thermal comfort in Zone during occupation time

        zone (simuplot.data.Zone): Zone to evaluate
        ref_temp (float): Reference maximum temperature

        Returns (pct_over, max_temp)
        pct_over (float): percentage of time over ref max temp
        max_temp (float): maximum temperature in the zone

        Returns (None, None) if Zone operative temperature or people count
        is missing, or if Zone has no occupation
    """

    try:
        # Get variable OPERATIVE_TEMPERATURE in zone
        # Get PEOPLE_COUNT to determine zone occupation status
        op_temps = zone.get_array(
            'OPERATIVE_TEMPERATURE', 'HOUR').values()
        nb_people = zone.get_array(
            'PEOPLE_COUNT', 'HOUR').values()
    except DataZoneError:
        # Return None as thermal confort % and None as max temperature
        return None, None
    else:

        # Create 0/1 presence scenario from nb_people
        io_people = np.where(nb_people > 0, 1, 0)

        # If occupation is always 0 (zone always empty),
        # return None as thermal confort % and None as max temperature
        nb_h_occup = np.count_nonzero(io_people)
        if nb_h_occup == 0:
            return None, None

        # Create array of temperatures during occupation
        occ_temp = io_people * op_temps

        # Determine maximum temperature during occupation
        max_temp = np.amax(occ_temp)

        # Computing % of time when temperature is above reference temp
        pct_over = 100 * np.count_nonzero(occ_temp > ref_temp) / nb_h_occup

        # Return % and maximum temperature in occupation [°C]
        return round(float(pct_over), 2), round(float(max_temp), 1)


class ThermalComfortHistog(DataPlotter):

    def __init__(self, building, color_chart):

        super(ThermalComfortHistog, self).__init__(building, color_chart)

        self._name = self.tr("Summer thermal comfort per zone")

        # Reference temperature
        self._ref_temp = None

        # Set column number and add headers
        self.dataTable.setColumnCount(3)
        self.dataTable.setHorizontalHeaderLabels([
            self.tr('Zone'),
            self.tr('Discomfort[%]'),
            self.tr('Max temp [°C]')
            ])
        self.dataTable.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)

        # Initialize climaticZoneSelectBox
        for dat in RT_CLIMATIC_ZONE:
            self.climaticZoneSelectBox.addItem(dat)

        # Initialize hqeStudyTypeSelectBox
        for dat in HQE_TMAX_PER_USAGE:
            self.hqeStudyTypeSelectBox.addItem(dat)

        # Refresh plot when zone is clicked/unclicked or sort order changed
        self.dataTable.itemClicked.connect(self.refresh_plot)
        self.dataTable.horizontalHeader().sectionClicked.connect(
            self.refresh_plot)

        # Refresh plot when RT_CLIMATIC_ZONE is changed
        self.climaticZoneSelectBox.activated.connect(
            self.refresh_plot)

        # Refresh data when maximum comfort temperature is changed
        self.hqeStudyRadioButton.clicked.connect(self.refresh_data)
        self.customStudyRadioButton.clicked.connect(self.refresh_data)
        self.hqeStudyTypeSelectBox.activated.connect(self.refresh_data)
        self.customStudySpinBox.valueChanged.connect(self.refresh_data)

    @property
    def name(self):
        return self._name

    @QtCore.pyqtSlot()
    def refresh_data(self):

        # Get zones in building
        zones = self._building.zones

        # Clear table and disable sorting before populating the table
        self.dataTable.clearContents()
        self.dataTable.setSortingEnabled(False)

        # Create one empty row per zone
        self.dataTable.setRowCount(len(zones))

        # Get reference temperature for thermal comfort
        if self.hqeStudyRadioButton.isChecked():
            self._ref_temp = \
                HQE_TMAX_PER_USAGE[self.hqeStudyTypeSelectBox.currentText()]
        else:
            self._ref_temp = self.customStudySpinBox.value()

        # For each zone
        for i, name in enumerate(zones):

            # Compute all comfort and max temperature
            pct_over, max_temp = eval_thermal_comfort(
                self._building.get_zone(name), self._ref_temp)

            # First column: zone name + checkbox
            name_item = QtGui.QTableWidgetItem(name)
            # If comfort values known, make zone checkable and check it
            if pct_over != None:
                name_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                                   QtCore.Qt.ItemIsEnabled)
                name_item.setCheckState(QtCore.Qt.Checked)

            # Second column: % thermal comfort
            val_item1 = QtGui.QTableWidgetItem()
            val_item1.setData(QtCore.Qt.DisplayRole, pct_over)

            val_item1.setFlags(QtCore.Qt.ItemIsEnabled)

            # Third column: zone max temperature in occupation
            val_item2 = QtGui.QTableWidgetItem()
            val_item2.setData(QtCore.Qt.DisplayRole, max_temp)

            val_item2.setFlags(QtCore.Qt.ItemIsEnabled)

            # Add items to row, column
            self.dataTable.setItem(i, 0, name_item)
            self.dataTable.setItem(i, 1, val_item1)
            self.dataTable.setItem(i, 2, val_item2)

        # Sort by value, descending order, and allow user column sorting
        self.dataTable.sortItems(1, QtCore.Qt.DescendingOrder)
        self.dataTable.setSortingEnabled(True)

        # Draw plot
        self.refresh_plot()

    @QtCore.pyqtSlot()
    def refresh_plot(self):

        vals = []
        names = []

        canvas = self.plotWidget.canvas

        # Clear axes
        canvas.axes.cla()
        canvas.set_tight_layout_on_resize(False)

        # Get checked rows and corresponding (name, value)
        for i in range(self.dataTable.rowCount()):
            if self.dataTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                name = self.dataTable.item(i, 0).text()
                names.append(name)
                try:
                    value = float(self.dataTable.item(i, 1).text())
                except AttributeError:
                    raise DataPlotterError(self.tr(
                        'Invalid discomfort value type for row {} ({}): {}'
                        ).format(i, name, self.dataTable.item(i, 1)))
                except ValueError:
                    raise DataPlotterError(self.tr(
                        'Invalid discomfort value for row {} ({}): {}'
                        ).format(i, name, self.dataTable.item(i, 1).text()))
                else:
                    vals.append(value)

        # If no data in vals, no zone was checked. Do not plot anything.
        if vals != []:

            # Store values as np array
            values = np.array(vals)

            # TODO: shall we display HQE levels if not in HQE mode ?

            # Get "Performant" and "Très Performant" levels
            self._hqep = RT_CLIMATIC_ZONE[unicode(
                self.climaticZoneSelectBox.currentText())][0]
            self._hqetp = RT_CLIMATIC_ZONE[unicode(
                self.climaticZoneSelectBox.currentText())][1]

            # Create and draw bar chart
            ind = np.arange(values.size)
            rectangle = canvas.axes.bar(ind, values, edgecolor='white')

            # Create rectangle color map
            rect_colors = np.where(values < self._hqetp, '#8EC02F', '#E47823')
            rect_colors[values > self._hqep] = '#868786'

            # Set rectangle color
            for rec, val in zip(rectangle, rect_colors):
                rec.set_color(val)

            # Adding values on top of rectangles
            for rect in rectangle:
                height = rect.get_height()
                canvas.axes.text(rect.get_x()+rect.get_width()/2.,
                                 1.0 * height,
                                 '{:.1f}'.format(height),
                                 size='smaller',
                                 style='italic',
                                 ha='center',
                                 va='bottom')

            # Add text for labels, title and axes ticks
            canvas.axes.set_ylabel(self.tr(
                '% time beyond {}°C').format(self._ref_temp))
            canvas.axes.set_xticks(ind + rectangle[0].get_width()/2)
            canvas.axes.set_xticklabels(names, ind, ha='right', rotation=75)

            # Plot "Très performant" and "Performant" values
            # Create x vector ind2 and y vectors dr_*
            ind2 = np.append(ind, values.size)
            dr_hqep = np.ones(len(ind2)) * self._hqep
            dr_hqetp = np.ones(len(ind2)) * self._hqetp
            # Plot lines
            canvas.axes.plot(ind2,
                             dr_hqetp,
                             '--',
                             color='#8EC02F',
                             linewidth=2,
                             label=self.tr(
                                 '{:.1f}% TP level').format(self._hqetp))
            canvas.axes.plot(ind2,
                             dr_hqep,
                             '--',
                             color='#E47823',
                             linewidth=2,
                             label=self.tr(
                                 '{:.1f}% P level').format(self._hqep))

            # Add legend
            l = canvas.axes.legend()
            l.texts[0].set_color('#8EC02F')
            l.texts[1].set_color('#E47823')
            l.texts[0].set_style('italic')

            # Set title
            canvas.axes.set_title(self.tr('Summer thermal comfort'))

            canvas.set_tight_layout_on_resize(True)

        # Draw plot
        canvas.draw()

