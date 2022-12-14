from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np

from .dataplotter import DataPlotter

from simuplot.data import (DATATYPES, SEASONS, TimeInterval,
                           DataZoneError, DataArrayIndexError)

HEAT_SOURCES = ['HEATING_RATE',
                'PEOPLE_HEATING_RATE',
                'LIGHTING_HEATING_RATE',
                'EQUIPMENT_HEATING_RATE',
                'WINDOWS_HEATING_RATE',
                'OPAQUE_SURFACES_HEATING_RATE',
                'INFILTRATION_HEATING_RATE',
               ]

class HeatGainPie(DataPlotter):

    def __init__(self, building, color_chart):

        super(HeatGainPie, self).__init__(building, color_chart)

        self._name = self.tr("Heat gains per source")

        # Results dict
        self._heat_build_zone = None

        # Set column number and add headers
        self.dataTable.setColumnCount(2)
        self.dataTable.setHorizontalHeaderLabels(
            [self.tr('Heat sources'), self.tr('Heat gains [kWh]')])
        self.dataTable.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)

        # Initialize table with one row per heat source with checkbox
        self.dataTable.setRowCount(len(HEAT_SOURCES))
        for i, val in enumerate(HEAT_SOURCES):
            # DATATYPES is a dict of type:(unit, string)
            hs_name = QtCore.QCoreApplication.translate(
                'Data', DATATYPES[val][1])
            name_item = QtWidgets.QTableWidgetItem(hs_name)
            name_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                               QtCore.Qt.ItemIsEnabled)
            name_item.setCheckState(QtCore.Qt.Checked)

            self.dataTable.setItem(i, 0, name_item)

        # Set periodSelectBox
        for per in SEASONS:
            self.periodSelectBox.addItem(
                QtCore.QCoreApplication.translate('Data', per[0]))

        # Refresh data when periodSelectBox is activated
        self.periodSelectBox.activated.connect(self.refresh_data)

        # Refresh plot when zoneSelectBox is modified
        self.zoneSelectBox.activated.connect(self.refresh_table_and_plot)

        # Refresh plot when zone is clicked/unclicked
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

        # Make TimeInterval from study period in combobox
        t_int = TimeInterval.from_string_seq(
            SEASONS[self.periodSelectBox.currentIndex()][1])

        # Compute heat gain per source in each zone
        self._heat_build_zone = {}
        for name in zones:
            zone = self._building.get_zone(name)
            # Compute heat gains for desired study period
            self._heat_build_zone[name] = {}
            for hs in HEAT_SOURCES:
                try:
                    # Sum values for heat source on time interval
                    # and convert result from [Wh] to [kWh]
                    heat_gains = zone.get_array(hs, 'HOUR').sum(t_int) / 1000
                except DataZoneError:
                    # If hourly heat source data not available,
                    #"mark it zero, Donnie"
                    heat_gains = 0
                except DataArrayIndexError:
                    self.warning.emit(self.tr(
                        'Hourly {} data for Zone {} is not one year long'
                        ).format(hs, name))
                    heat_gains = 0
                self._heat_build_zone[name][hs] = heat_gains

        # Compute heat gain per source for building by summing all zones
        self._heat_build_zone['Building'] = {}
        for hs in HEAT_SOURCES:
            self._heat_build_zone['Building'][hs] = \
                sum([self._heat_build_zone[zone][hs] for zone in zones])

        # Write in Table and draw plot
        self.refresh_table_and_plot()

    @QtCore.pyqtSlot()
    def refresh_table_and_plot(self):

        # Current zone or building displayed
        if (self.zoneSelectBox.currentIndex() ==
                self.zoneSelectBox.count() - 1):
            cur_zone = 'Building'
        else:
            cur_zone = self.zoneSelectBox.currentText()

        # Display Zone or building value in table 2nd column
        for i, hs in enumerate(HEAT_SOURCES):

            # Get current heat gains for heat source in the zone
            hs_value = int(self._heat_build_zone[cur_zone][hs])

            # Set item value for 2nd column
            val_item = QtWidgets.QTableWidgetItem()
            val_item.setData(QtCore.Qt.DisplayRole, hs_value)
            val_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.dataTable.setItem(i, 1, val_item)

            # Uncheck heat source name if value is zero
            name_item = self.dataTable.item(i, 0)
            if hs_value == 0:
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

        # Compute heat source sum and
        # create plot list removing unchecked values
        name_plot = []
        value_plot = []
        sum_value = 0
        for i in range(self.dataTable.rowCount()):
            value = int(self.dataTable.item(i, 1).text())
            sum_value += value
            if self.dataTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                name_plot.append(self.dataTable.item(i, 0).text())
                value_plot.append(value)

        # If sum is 0, heat gain are 0. Do not plot anything.
        if sum_value != 0:

            # Create pie chart
            # (Make zone heat need non dimensional to avoid pie expansion)
            canvas.axes.pie(np.array(value_plot) / sum_value,
                            labels=name_plot,
                            colors=self._color_chart, autopct='%1.1f%%',
                            shadow=False, startangle=90,)
            canvas.axes.axis('equal')

            # Set title
            title_str = self.tr('Heat gains repartition')
            canvas.axes.set_title(title_str, y=1.05)

            canvas.set_tight_layout_on_resize(True)

        # Draw plot
        canvas.draw()

