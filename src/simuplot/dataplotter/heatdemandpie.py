from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np

from .dataplotter import DataPlotter, DataPlotterError

from simuplot.data import DataZoneError

class HeatDemandPie(DataPlotter):

    def __init__(self, building, color_chart):

        super(HeatDemandPie, self).__init__(building, color_chart)

        self._name = self.tr("Heat demand per zone")

        # Initialize total building heat need
        self._build_total_hn = 0

        # Set column number and add headers
        self.dataTable.setColumnCount(2)
        self.dataTable.setHorizontalHeaderLabels(
            [self.tr('Zone'), self.tr('Heat need [kWh]')])
        self.dataTable.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)

        # Refresh plot when zone is clicked/unclicked or sort order changed
        self.dataTable.itemClicked.connect(self.refresh_plot)
        self.dataTable.horizontalHeader().sectionClicked.connect(
            self.refresh_plot)

    @property
    def name(self):
        return self._name

    @QtCore.pyqtSlot()
    def refresh_data(self):

        # Reset total building heat need
        self._build_total_hn = 0

        # Get zones in building
        zones = self._building.zones

        # Clear table and disable sorting before populating the table
        self.dataTable.clearContents()
        self.dataTable.setSortingEnabled(False)

        # Create one empty row per zone
        self.dataTable.setRowCount(len(zones))

        # For each zone
        for i, name in enumerate(zones):

            # Compute heat demand for zone
            zone = self._building.get_zone(name)
            try:
                # Get Array for Variable HEATING_RATE in Zone
                # Hourly power [W] is equivalent to Hourly energy [Wh]
                vals_array = zone.get_array('HEATING_RATE', 'HOUR')
            except DataZoneError:
                heat_demand = 0
            else:
                # Convert total heat need [Wh] -> [kWh]
                # TODO: int or float ? explicit rounding ?
                heat_demand = int(vals_array.sum() / 1000)

            # Add zone heat demand to total heat need
            self._build_total_hn += heat_demand

            # Firts column: zone name + checkbox
            name_item = QtWidgets.QTableWidgetItem(name)

            name_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                               QtCore.Qt.ItemIsEnabled)

            # By default, display zone on chart only if value not 0
            if heat_demand != 0:
                name_item.setCheckState(QtCore.Qt.Checked)
            else:
                name_item.setCheckState(QtCore.Qt.Unchecked)

            # Second column: heat need value
            val_item = QtWidgets.QTableWidgetItem()
            val_item.setData(QtCore.Qt.DisplayRole, heat_demand)

            val_item.setFlags(QtCore.Qt.ItemIsEnabled)

            # Add items to row, column
            self.dataTable.setItem(i, 0, name_item)
            self.dataTable.setItem(i, 1, val_item)

        # Sort by value, descending order, and allow user column sorting
        self.dataTable.sortItems(1, QtCore.Qt.DescendingOrder)
        self.dataTable.setSortingEnabled(True)

        # Draw plot
        self.refresh_plot()

    @QtCore.pyqtSlot()
    def refresh_plot(self):

        canvas = self.plotWidget.canvas

        # Clear axes
        canvas.axes.cla()
        canvas.set_tight_layout_on_resize(False)

        # Get checked rows and corresponding (name, value)
        values = []
        names = []
        for i in range(self.dataTable.rowCount()):
            if self.dataTable.item(i, 0).checkState() == QtCore.Qt.Checked:
                name = self.dataTable.item(i, 0).text()
                names.append(name)
                try:
                    value = int(self.dataTable.item(i, 1).text())
                except AttributeError:
                    raise DataPlotterError(self.tr(
                        'Invalid cons value type for row {} ({}): {}'
                        ).format(i, name, self.dataTable.item(i, 1)))
                except ValueError:
                    raise DataPlotterError(self.tr(
                        'Invalid cons value for row {} ({}): {}'
                        ).format(i, name, self.dataTable.item(i, 1).text()))
                else:
                    values.append(value)

        # If total heat need is 0, do not plot anything.
        if self._build_total_hn != 0:

            # Create pie chart
            # (Make zone heat need non dimensional to avoid pie expansion)
            canvas.axes.pie(np.array(values) / self._build_total_hn,
                            labels=names,
                            colors=self._color_chart, autopct='%1.1f%%',
                            shadow=False, startangle=90)
            canvas.axes.axis('equal')

            # Set title
            title_str = self.tr(
                'Building heat need: {} [kWh]').format(self._build_total_hn)
            canvas.axes.set_title(title_str, y=1.05)

            canvas.set_tight_layout_on_resize(True)

        # Draw plot
        canvas.draw()

