# -*- coding: utf-8 -*-

import numpy as np

from PyQt4 import QtCore

from PyQt4.QtCore import QT_TRANSLATE_NOOP as translate

DataTypes = {
    'AIR_DRYBULB_TEMPERATURE':
        ('°C', translate('Data', 'Air dry-bulb temperature')),
    'AIR_WETBULB_TEMPERATURE':
        ('°C', translate('Data', 'Air wet-bulb temperature')),
    'AIR_HUMIDITY_RATIO':
        ('%', translate('Data', 'Relative humidity')),
    'OPERATIVE_TEMPERATURE':
        ('°C', translate('Data', 'Operative temperature')),
    'DIFFUSE_SOLAR_RADIATION':
        ('W/m2', translate('Data', 'Diffuse solar radiation')),
    'DIRECT_SOLAR_RADIATION':
        ('W/m2', translate('Data', 'Direct solar radiation')),
    'HEATING_RATE':
        ('W', translate('Data', 'Heating rate')),
    'COOLING_RATE':
        ('W', translate('Data', 'Cooling rate')),
    'PEOPLE_COUNT':
        ('', translate('Data', 'People count')),
    'PEOPLE_HEATING_RATE':
        ('W', translate('Data', 'People heating rate')),
    'LIGHTING_HEATING_RATE':
        ('W', translate('Data', 'Lighting heating rate')),
    'EQUIPMENT_HEATING_RATE':
        ('W', translate('Data', 'Equipment heating rate')),
    'WINDOWS_HEATING_RATE':
        ('W', translate('Data', 'Windows heating rate')),
    'OPAQUE_SURFACES_HEATING_RATE':
        ('W', translate('Data', 'Opaque surfaces heating rate')),
    'INFILTRATION_HEATING_RATE':
        ('W', translate('Data', 'Infiltrations heating rate')),
}

DataPeriods = [
    'HOUR',
    'DAY',
    'MONTH',
    'YEAR',
]

class Variable(QtCore.QObject):
    """Stores an array of values for one physical parameter (temperature,
       heat demand,...)
    """

    def __init__(self, data_type):
    
        super(Variable, self).__init__()

        # Data type
        if data_type not in DataTypes:
            raise DataVariableTypeError(self.tr(
                'Incorrect data type {}'
                ).format(data_type).encode('utf-8'))
        self._data_type = data_type
        
        # Values for each sampling period
        self._values = {}
        
        # TODO: Start time
        # Which datatype for time?
        # For now, we'll suppose that all outputs 
        # start at "01/01  01:00:00"
        # self.date_start = None
        
    def __str__(self):
        return 'Variable "{}": {}'.format(self._data_type, self._values)
    
    @property
    def data_type(self):
        return self._data_type

    @property
    def periods(self):
        """Return list of periods for which Variable holds a set of value"""
        return self._values.keys()

    def get_values(self, period):
        if period not in DataPeriods:
            raise DataVariablePeriodError(self.tr(
                'Incorrect sample period {}'
                ).format(period).encode('utf-8'))
        try:
            return self._values[period]
        except KeyError:
            raise DataVariableNoValueError(self.tr(
                'No value for sample period {}'
                ).format(period).encode('utf-8'))

    def set_values(self, period, array):
        """Set val_list as values
            
            val_list: list of numbers in numeric or string format
        """
        if period not in DataPeriods:
            raise DataVariablePeriodError(self.tr(
                'Incorrect sample period {}'
                ).format(period).encode('utf-8'))
        
        self._values[period] = array
    
# TODO: Multi-buildings / Multi-versions
# class Project(QtCore.QObject):
# 
#     def __init__(self):
#     
#         super(Project, self).__init__()
#
#         self.variants = {}
# 
# class ProjectVariant(QtCore.QObject):
# 
#     def __init__(self):
# 
#         super(ProjectVariant, self).__init__()
#
#         self.name = []
#         self.buildings = {}

class Building(QtCore.QObject):

    def __init__(self, name):
    
        super(Building, self).__init__()

        self._name = name
        self._zones = {}
        self._environment = None

    @property
    def name(self):
        return self._name

    @property
    def zones(self):
        """Return zone names"""
        return self._zones.keys()

    def get_zone(self, name):
        try:
            return self._zones[name]
        except KeyError:
            raise DataBuildingError(self.tr(
                'Zone {} not in Building'
                ).format(name).encode('utf-8'))

    def add_zone(self, name):
        if name in self._zones:
            raise DataBuildingError(self.tr(
                'Zone {} already in Building'
                ).format(name).encode('utf-8'))
        else:
            z = Zone(name)
            self._zones[name] = z
            return z

    def del_zone(self, name):
        try:
            del self._zones[name]
        except KeyError:
            raise DataBuildingError(self.tr(
                'Zone {} not in Building'
                ).format(name).encode('utf-8'))

    def get_environment(self):
        return self._environment

    def add_environment(self):
        if self._environment is not None:
            raise DataBuildingError(self.tr(
                'Environment zone already in Building'
                ).encode('utf-8'))
        else:
            o = Zone(self.tr('Environment'))
            self._environment = o
            return o

    def del_environment(self):
        self._environment = None

    def clean(self):
        self._zones = {}
        self._environment = None

class Zone(QtCore.QObject):
    """Define a thermal zone
    
       Public attributes:
       - name (str): name of the Zone
       - variables (str list): variable types available for the Zone

       Public methods:
       - get_variable_periods
       - get_values
       - set_values
       """

    def __init__(self, name):
        
        super(Zone, self).__init__()

        self._name = name
        self._variables = {}
        #self.surfaces = {}

    @property
    def name(self):
        return self._name

    @property
    def variables(self):
        """Return variable names"""
        return self._variables.keys()

    def _get_variable(self, data_type):
        """Return variable of type data_type"""
        try:
            return self._variables[data_type]
        except KeyError:
            raise DataZoneError(self.tr(
                'Variable {} not in Zone {}'
                ).format(data_type, self._name).encode('utf-8'))

    def _add_variable(self, data_type):
        """Add variable of type data_type"""
        if data_type in self._variables:
            raise DataZoneError(self.tr(
                'Variable {} already in Zone {}'
                ).format(data_type, self._name).encode('utf-8'))
        else:
            try:
                var = Variable(data_type)
            except DataVariableTypeError as e:
                raise DataZoneError(e)
            else:
                self._variables[data_type] = var
                return var
        
    def _del_variable(self, data_type):

        try:
            del self._variables[data_type]
        except KeyError:
            raise DataZoneError(self.tr(
                'Variable {} not in Zone {}'
                ).format(data_type, self._name).encode('utf-8'))

    def get_variable_periods(self, data_type):
        """Return list of available periods for type data_type"""
        self._get_variable(data_type).periods

    def get_values(self, data_type, period):
        """Return values of variable of type data_type for period"""
        try:
            var = self._variables[data_type]
        except KeyError:
            raise DataZoneError(self.tr(
                'Variable {} not in Zone {}'
                ).format(data_type, self._name).encode('utf-8'))
        try:
            return var.get_values(period)
        except DataVariablePeriodError as e:
            raise DataZoneError(e + self.tr(
                'while getting values for {} in Zone {}'
                ).format(data_type, self._name).encode('utf-8'))
        except DataVariableNoValueError:
            raise DataZoneError(self.tr(
                'No {} data for {} in Zone {}'
                ).format(period, data_type, self._name).encode('utf-8'))

    def set_values(self, data_type, period, array):
        """Set values of variable of type data_type for period
        
            data_type (str): data type
            period (str): period
            array (numpy array): array of values
            """
        if data_type in self.variables:
            var = self._variables[data_type]
        else:
            var = self._add_variable(data_type)
        
        try:
            var.set_values(period, array)
        except DataVariablePeriodError as e:
            raise DataZoneError(str(e) + self.tr(
                ' while setting values for {} in Zone {}'
                ).format(data_type, self._name).encode('utf-8'))

# class Surface(QtCore.QObject):
#     """Defines an enveloppe element through which heat is loss"""
# 
#     def __init__(self, name, surf, surf_type):
#     
#         super(Surface, self).__init__()
#
#         self._name = name
#         self._surf = 0
#         # surf_type can be WALL, ROOF, FLOOR, WINDOW
#         self._surf_type = surf_type
#

class DataError(Exception):
    pass

class DataVariableError(DataError):
    pass

class DataVariableTypeError(DataVariableError):
    """Data type does not exist"""
    pass

class DataVariablePeriodError(DataVariableError):
    """Data sample period does not exist"""
    pass

class DataVariableNoValueError(DataVariableError):
    """Requested value is not available"""
    pass

class DataBuildingError(DataError):
    pass

class DataZoneError(DataError):
    pass

