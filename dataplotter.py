# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from data import DataZoneError

class DataPlotter(QtCore.QObject):
    """Virtual class

       Useless by itself. Implement in sub-clases
    """
    
    def __init__(self, building, color_chart):
        
        super(DataPlotter, self).__init__()

        # Reference to building isntance
        self._building = building

        # Get color chart
        self._color_chart = color_chart

    def refresh_data(self):
        raise NotImplementedError

class ConsPerZonePieDataPlotter(DataPlotter):

    @staticmethod
    def ComputeZoneCons(zone):
        try:
            # Get variable HEATING_RATE in zone
            # Hourly power [W] is equivalent to Hourly energy [Wh]
            vals = zone.get_variable('HEATING_RATE', 'HOUR')
        except DataZoneError:
            # TODO: log warning
            return 0
        else:
            # Return total consumption [kWh]
            return vals.sum() / 1000
        
    def __init__(self, MplWidget, TableWidget, building, color_chart):
        
        super(ConsPerZonePieDataPlotter, self).__init__(building, color_chart)
        
        # Chart widget
        self._MplWidget = MplWidget
        # Table widget
        self._table_widget = TableWidget

        # Set column number and add headers
        self._table_widget.setColumnCount(2)
        self._table_widget.setHorizontalHeaderLabels(['Zone', 
                                                      'Consumption [kWh]'])
        
        # Refresh plot when zone is clicked/unclicked or sort order changed
        self._table_widget.itemClicked.connect(self.refresh_plot)
        self._table_widget.horizontalHeader().sectionClicked.connect( \
            self.refresh_plot)

    def refresh_data(self):
        
        # Get zones in building
        zones = self._building.zones
        
        # Clear table
        self._table_widget.clearContents()
        
        # Create one empty row per zone
        self._table_widget.setRowCount(len(zones))
        
        # For each zone
        for i, name in enumerate(zones):

            # Compute total consumption
            # TODO: int or float ? explicit rounding ?
            cons = int(self.ComputeZoneCons(zones[name]))

            # Firts column: zone name + checkbox
            name_item = QtGui.QTableWidgetItem(name)

            name_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                               QtCore.Qt.ItemIsEnabled)

            # By default, display zone on chart only if value not 0
            if cons != 0:
                name_item.setCheckState(QtCore.Qt.Checked)
            else:
                name_item.setCheckState(QtCore.Qt.Unchecked)

            # Second column: consumption value
            val_item = QtGui.QTableWidgetItem()
            val_item.setData(QtCore.Qt.DisplayRole, cons)
            
            val_item.setFlags(QtCore.Qt.ItemIsEnabled)

            # Add items to row, column
            self._table_widget.setItem(i, 0, name_item)
            self._table_widget.setItem(i, 1, val_item)

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
                names.append(self._table_widget.item(i,0).text())
                values.append(int(self._table_widget.item(i,1).text()))
        
        # Clear axes
        self._MplWidget.canvas.axes.cla()
    
        # Create and draw pie chart
        self._MplWidget.canvas.axes.pie(values, labels=names, 
            colors=self._color_chart, autopct='%1.1f%%', 
            shadow=False, startangle=90)
        self._MplWidget.canvas.axes.axis('equal')
        self._MplWidget.canvas.draw()

