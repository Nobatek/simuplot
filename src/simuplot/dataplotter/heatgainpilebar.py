# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from PyQt4 import QtCore, QtGui

import numpy as np

from .dataplotter import DataPlotter

from simuplot.data import DATATYPES, DataZoneError, MONTHS, TimeInterval

HEAT_SOURCES = ['HEATING_RATE',
                'PEOPLE_HEATING_RATE',
                'LIGHTING_HEATING_RATE',
                'EQUIPMENT_HEATING_RATE',
                'WINDOWS_HEATING_RATE',
                'OPAQUE_SURFACES_HEATING_RATE',
                'INFILTRATION_HEATING_RATE',
               ]

class HeatGainPileBar(DataPlotter):

    def __init__(self, building, color_chart):

        super(HeatGainPileBar, self).__init__(building, color_chart)

        self._name = self.tr("Heat gains per month")

        # Results dict
        self._heat_build_zone = None

        # Set column number and add headers
        self.dataTable.setColumnCount(13)
        self.dataTable.setHorizontalHeaderLabels(
            [self.tr('Heat sources')] + [m[0] for m in MONTHS])
        self.dataTable.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)

        # Initialize table with one row per heat source with checkbox
        self.dataTable.setRowCount(len(HEAT_SOURCES))
        for i, val in enumerate(HEAT_SOURCES):
            # DATATYPES is a dict of type:(unit, string)
            hs_name = QtCore.QCoreApplication.translate(
                'Data', DATATYPES[val][1])
            name_item = QtGui.QTableWidgetItem(hs_name)
            name_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                               QtCore.Qt.ItemIsEnabled)
            name_item.setCheckState(QtCore.Qt.Checked)

            self.dataTable.setItem(i, 0, name_item)

        # Refresh plot when zoneSelectBox is modified
        self.zoneSelectBox.activated.connect(self.refresh_table_and_plot)

        # Refresh plot when zone is clicked/unclicked
        self.dataTable.itemClicked.connect(self.refresh_plot)

    @property
    def name(self):
        return self._name

    @QtCore.pyqtSlot()
    def refresh_data(self):

        # Get zones in building, sorted by name
        zones = self._building.zones
        zones.sort()

        # Set combobox with zone names
        # and add 'Building' as a ficticious "all zones" zone
        self.zoneSelectBox.clear()
        self.zoneSelectBox.addItems(zones)
        self.zoneSelectBox.addItem(self.tr('Building'))
        self.zoneSelectBox.setCurrentIndex(self.zoneSelectBox.count() - 1)

        # Compute heat gain per source in each zone
        self._heat_build_zone = {}
        for name in zones:
            zone = self._building.get_zone(name)
            # Compute heat gains for desired study period
            self._heat_build_zone[name] = {}
            for hs in HEAT_SOURCES:
                try:
                    # Get the Array object for current heat source
                    val_array = zone.get_array(hs, 'HOUR')
                except DataZoneError:
                    # If hourly heat source data not available,
                    # "mark it zero, Donnie", for each month
                    self._heat_build_zone[name][hs] = np.zeros(12)
                else:
                    # Create array of monthly energy in [kWh]
                    self._heat_build_zone[name][hs] = np.array(
                        [val_array.sum(TimeInterval.from_month_nb(m))
                         for m in range(len(MONTHS))]) / 1000

        # Compute heat gain per source for building by summing all zones
        self._heat_build_zone['Building'] = {}
        if len(zones):
            for hs in HEAT_SOURCES:
                self._heat_build_zone['Building'][hs] = np.sum(
                    [self._heat_build_zone[zone][hs] for zone in zones],
                    axis=0)
        else:
            # If no Zone data, set 0 values to Building for each source
            for hs in HEAT_SOURCES:
                self._heat_build_zone['Building'][hs] = np.zeros(12)

        # Write in Table and draw plot
        self.refresh_table_and_plot()

    @QtCore.pyqtSlot()
    def refresh_table_and_plot(self):

        # Current zone or building displayed
        if self.zoneSelectBox.currentIndex() == self.zoneSelectBox.count() - 1:
            cur_zone = 'Building'
        else:
            cur_zone = self.zoneSelectBox.currentText()

        # Display Zone or building values in table
        for i, hs in enumerate(HEAT_SOURCES):
            # Get current heat gains for heat source in the zone
            hs_value = self._heat_build_zone[cur_zone][hs]

            for j, monthly_val in enumerate(hs_value):
                # Set item value for month column
                val_item = QtGui.QTableWidgetItem()
                val_item.setData(QtCore.Qt.DisplayRole, int(monthly_val))
                val_item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.dataTable.setItem(i, j+1, val_item)

            # Uncheck heat source name if value is zero
            name_item = self.dataTable.item(i, 0)
            if np.sum(hs_value) == 0:
                name_item.setCheckState(QtCore.Qt.Unchecked)
            else:
                name_item.setCheckState(QtCore.Qt.Checked)

        # Draw plot
        self.refresh_plot()

    @QtCore.pyqtSlot()
    def refresh_plot(self):

        canvas = self.plotWidget.canvas

        # Clear axes
        canvas.axes.cla()
        canvas.set_tight_layout_on_resize(False)

        # Get all heat sources names
        hs_names = [self.dataTable.item(i, 0).text()
                    for i in range(self.dataTable.rowCount())]

        # Compute heat source sum and
        # create plot list removing unchecked values
        name_plot = []
        value_plot = []
        sum_values = 0
        for i in range(self.dataTable.rowCount()):

            month_vals = [int(self.dataTable.item(i, j).text())
                          for j in range(1, len(MONTHS)+1)]
            sum_values += np.sum(np.abs(month_vals))

            if self.dataTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                name_plot.append(self.dataTable.item(i, 0).text())
                value_plot.append(month_vals)

        # If sum is 0, heat gains and losses are 0. Do not plot anything.
        if sum_values != 0:

            # Create a uniform x axis
            ind = np.arange(len(MONTHS))

            # Create a colormap adapted to HEAT_SOURCES
            # TODO: move to __init__ ?
            hs_cmap = {hs_names[i] : self._color_chart[i]
                       for i in range(len(HEAT_SOURCES))}

            # Create and draw bar chart
            prev_height = np.zeros(len(MONTHS))
            width = 0.8
            for i, (hs_name, hs_vals) in enumerate(zip(name_plot, value_plot)):
                canvas.axes.bar(ind,
                                hs_vals,
                                width=width,
                                edgecolor='white',
                                color=hs_cmap[hs_name],
                                bottom=prev_height,
                                label=hs_name)
                prev_height += np.array(hs_vals)

            # Add text for labels, title and axes ticks
            canvas.axes.set_ylabel(self.tr('Heat gains / loss [kWh]'))
            canvas.axes.set_xticks(ind + width/2)
            canvas.axes.set_xticklabels([m[0] for m in MONTHS],
                                        ind, ha='center')

            # Set title
            title_str = self.tr('Heat gains repartition')
            canvas.axes.set_title(title_str, y=1.05)

            # Add legend
            legend = canvas.axes.legend(loc='upper center',
                                        bbox_to_anchor=(0.5, -0.05),
                                        fancybox=True, ncol=4)
            for text in legend.texts:
                text.set_size('small')

            canvas.set_tight_layout_on_resize(False)

        # Draw plot
        canvas.draw()

