# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QT_TRANSLATE_NOOP as translate

import numpy as np

from .dataplotter import DataPlotter, DataPlotterError

from simuplot.data import DataZoneError

RT_CLIMATIC_ZONE = [
    ('H1a - H1b - H2a - H2b', [2, 1]),
    ('H1c - H2c', [2.5, 1.5]),
    ('H2d - H3', [3, 2]),
]

HQE_TMAX_PER_USAGE = [
    ('Bureau - Enseignement', 28),
    ('Hôtel', 26),
    ('Commun - Circulation commerce et baignade', 30),
    ('Entrepôts', 35),
]

STUDY_TYPES = [
    ('CUSTOM', translate('ThermalComfortHistog', 'Custom study')),
    ('HQE', translate('ThermalComfortHistog', 'HQE study')),
    ]

COLORS = {
    'BASE': '#868786',
    'GOOD': '#E47823',
    'BETTER': '#8EC02F',
    }

# TODO: set level 1 max value according to level 2 value / enabled state
# and conversely

# TODO: optimize code to avoid refreshing plot so many times


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

        # Initialize studyTypeSelectBox
        for _, type_name in STUDY_TYPES:
            self.studyTypeSelectBox.addItem(self.tr(type_name))

        # Initialize HQE parameters box
        self.hqeParametersBox.hide()
        for name, _ in RT_CLIMATIC_ZONE:
            self.hqeClimaticZoneSelectBox.addItem(name)
        for name, _ in HQE_TMAX_PER_USAGE:
            self.hqeZoneTypeSelectBox.addItem(name)

        # Connect GUI signals
        self.comfortLevel1CheckBox.stateChanged.connect(
            self.comfortLevel1NameEdit.setEnabled)
        self.comfortLevel1CheckBox.stateChanged.connect(
            self.comfortLevel1DoubleSpinBox.setEnabled)
        self.comfortLevel2CheckBox.stateChanged.connect(
            self.comfortLevel2NameEdit.setEnabled)
        self.comfortLevel2CheckBox.stateChanged.connect(
            self.comfortLevel2DoubleSpinBox.setEnabled)

        self.studyTypeSelectBox.currentIndexChanged.connect(
            self.study_type_changed)
        self.hqeZoneTypeSelectBox.currentIndexChanged.connect(
            self.hqe_zone_type_changed)
        self.hqeClimaticZoneSelectBox.currentIndexChanged.connect(
            self.rt_climatic_zone_changed)

        # Refresh data when maximum comfort temperature is changed
        self.maxComfortTemperatureDoubleSpinBox.valueChanged.connect(
            self.refresh_data)

        # Refresh plot when zone is clicked/unclicked or sort order changed
        self.dataTable.itemClicked.connect(self.refresh_plot)
        self.dataTable.horizontalHeader().sectionClicked.connect(
            self.refresh_plot)

        # Refresh plot when comfort levels are changed
        self.comfortLevel1DoubleSpinBox.valueChanged.connect(self.refresh_plot)
        self.comfortLevel2DoubleSpinBox.valueChanged.connect(self.refresh_plot)
        self.comfortLevel1CheckBox.clicked.connect(self.refresh_plot)
        self.comfortLevel2CheckBox.clicked.connect(self.refresh_plot)
        self.comfortLevel1NameEdit.editingFinished.connect(
            self._level_names_editing_finished)
        self.comfortLevel2NameEdit.editingFinished.connect(
            self._level_names_editing_finished)

    @property
    def name(self):
        return self._name

    def _level_names_editing_finished(self):
        # When leaving LineEdit widget,
        # refresh plot only if text was really modified
        if (self.comfortLevel1NameEdit.isModified() or
            self.comfortLevel2NameEdit.isModified()):
            self.comfortLevel1NameEdit.setModified(False)
            self.comfortLevel2NameEdit.setModified(False)
            self.refresh_plot()

    @QtCore.pyqtSlot(int)
    def study_type_changed(self, index):

        study_type, _ = STUDY_TYPES[index]

        def set_comfort_conditions_widgets_enabled(enable):
            # Enable/disable widgets in the "Comfort conditions" box
            # typically to disable them if study type is not custom
            self.maxComfortTemperatureDoubleSpinBox.setEnabled(enable)
            self.comfortLevel1DoubleSpinBox.setEnabled(enable)
            self.comfortLevel2DoubleSpinBox.setEnabled(enable)
            self.comfortLevel1CheckBox.setEnabled(enable)
            self.comfortLevel2CheckBox.setEnabled(enable)
            self.comfortLevel1NameEdit.setEnabled(enable)
            self.comfortLevel2NameEdit.setEnabled(enable)

        if study_type == 'HQE':

            # Set comfort temperature and levels
            self.hqe_zone_type_changed(
                self.hqeZoneTypeSelectBox.currentIndex())
            self.rt_climatic_zone_changed(
                self.hqeClimaticZoneSelectBox.currentIndex())
            # Show HQE parameters box
            self.hqeParametersBox.show()
            # Disable custom comfort conditions widgets
            set_comfort_conditions_widgets_enabled(False)
            # Set comfort conditions widgets with HQE values
            self.comfortLevel1CheckBox.setCheckState(QtCore.Qt.Checked)
            self.comfortLevel2CheckBox.setCheckState(QtCore.Qt.Checked)
            self.comfortLevel1NameEdit.setText(self.tr('P level'))
            self.comfortLevel2NameEdit.setText(self.tr('TP level'))
            # Force plot refresh in case comfort conditions were changed
            self.refresh_plot()

        else:

            self.hqeParametersBox.hide()
            set_comfort_conditions_widgets_enabled(True)

    @QtCore.pyqtSlot(int)
    def hqe_zone_type_changed(self, index):

        _, hqe_comf_temp = HQE_TMAX_PER_USAGE[index]
        self.maxComfortTemperatureDoubleSpinBox.setValue(hqe_comf_temp)

    @QtCore.pyqtSlot(int)
    def rt_climatic_zone_changed(self, index):

        _, hqe_comfort_levels = RT_CLIMATIC_ZONE[index]

        self.comfortLevel1DoubleSpinBox.setValue(hqe_comfort_levels[0])
        self.comfortLevel2DoubleSpinBox.setValue(hqe_comfort_levels[1])

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
        self._ref_temp = self.maxComfortTemperatureDoubleSpinBox.value()

        # For each zone
        for i, name in enumerate(zones):

            # Compute all comfort and max temperature
            pct_over, max_temp = eval_thermal_comfort(
                self._building.get_zone(name), self._ref_temp)

            # First column: zone name + checkbox
            name_item = QtGui.QTableWidgetItem(name)
            # If comfort values known, make zone checkable and check it
            if pct_over is not None:
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

            # Get comfort levels check states, values and names
            level_1_checked = self.comfortLevel1CheckBox.checkState()
            level_2_checked = self.comfortLevel2CheckBox.checkState()
            level_1 = self.comfortLevel1DoubleSpinBox.value()
            level_2 = self.comfortLevel2DoubleSpinBox.value()
            level_1_name = self.comfortLevel1NameEdit.text()
            level_2_name = self.comfortLevel2NameEdit.text()

            # Create and draw bar chart
            ind = np.arange(values.size)
            rectangle = canvas.axes.bar(ind, values, edgecolor='white')

            # Create rectangle color map
            rect_colors = np.array(values.size * [COLORS['BASE']])
            if level_1_checked:
                rect_colors[values < level_1] = COLORS['GOOD']
            if level_2_checked:
                rect_colors[values < level_2] = COLORS['BETTER']

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

            # Plot GOOD and BETTER level lines
            ind2 = np.append(ind, values.size)
            if level_1_checked:
                canvas.axes.plot(ind2,
                                 np.ones(len(ind2)) * level_1,
                                 '--',
                                 color=COLORS['GOOD'],
                                 linewidth=2,
                                 label=(('{:.1f}% ').format(level_1) +
                                        level_1_name))
            if level_2_checked:
                canvas.axes.plot(ind2,
                                 np.ones(len(ind2)) * level_2,
                                 '--',
                                 color=COLORS['BETTER'],
                                 linewidth=2,
                                 label=(('{:.1f}% ').format(level_2) +
                                        level_2_name))

            # Add legend
            if level_1_checked or level_2_checked:
                l = canvas.axes.legend()
                if level_1_checked:
                    l.texts[0].set_color(COLORS['GOOD'])
                    if level_2_checked:
                        l.texts[1].set_color(COLORS['BETTER'])
                else:
                    l.texts[0].set_color(COLORS['BETTER'])

            # Set title
            canvas.axes.set_title(self.tr('Summer thermal comfort'))

            canvas.set_tight_layout_on_resize(True)

        # Draw plot
        canvas.draw()
