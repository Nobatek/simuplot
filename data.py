# -*- coding: utf-8 -*-

import numpy as np

# TODO: unit conversion functions in DataReader
# TODO: do we need both HEATING_RATE and HEATING_DEMAND ?
DataTypes = {
    'AIR_DRYBULB_TEMPERATURE':'°C',
    'AIR_WETBULB_TEMPERATURE':'°C',
    'AIR_HUMIDITY_RATIO':'%',
    'OPERATIVE_TEMPERATURE':'°C',
    'HEATING_RATE':'W',
    'HEATING_DEMAND':'kWh',
    'DIFFUSE_SOLAR_RADIATION':'W/m2',
    'DIRECT_SOLAR_RADIATION':'W/m2',
    'PEOPLE_COUNT':'',
}

DataPeriods = [
    'HOUR',
    'DAY',
    'MONTH',
    'YEAR',
]

class Variable(object):
    """Stores an array of values for one physical parameter (temperature,
       heat demand,...
    """

    def __init__(self, data_type):
    
        # Data type
        if data_type not in DataTypes:
            raise DataVariableTypeError('Incorrect data type: %s' 
                                          % date_type)
        self._data_type = data_type
        
        # Values for each sampling period
        self._values = {period:None for period in DataPeriods}
        
        # TODO: Start time
        # Which datatype for time?
        # For now, we'll suppose that all outputs 
        # start at "01/01  01:00:00"
        # self.date_start = None
        
    def __str__(self):
        return 'Variable "%s": %s' % (self._data_type, self._values)
    
    @property
    def data_type(self):
        return self._data_type

    def get_values(self, period):
        try:
            return self._values[period]
        except KeyError:
            raise DataVariablePeriodError('Incorrect sample period: %s' 
                                          % period)

    def set_values_from_list(self, period, val_list):
        """Set val_list as values
            
            val_list: list of numbers in numeric or string format
        """
        try:
            self._values[period] = np.array(val_list, float)
        except KeyError:
            raise DataVariablePeriodError('Incorrect sample period: %s' 
                                          % period)
        except ValueError as e:
            raise DataVariableValueError(e)
    
# TODO: Multi-buildings / Multi-versions
# class Project(object):
# 
#     def __init__(self):
#     
#         self.variants = {}
# 
# class ProjectVariant(object):
# 
#     def __init__(self):
# 
#         self.name = []
#         self.buildings = {}

class Building(object):

    def __init__(self, name):
    
        self._name = name
        self._zones = {}
        self._environment = None

    @property
    def name(self):
        return self._name

    def get_zone(self, name):
        try:
            return self._zones[name]
        except KeyError:
            raise DataBuildingError('Zone %s not in Building' % name)

    @property
    def zones(self):
        return self._zones

    def get_environment(self):
        return self._environment

    def add_zone(self, name):
        if name in self._zones:
            raise DataBuildingError('Zone %s already in Building' % name)
        else:
            z = Zone(name)
            self._zones[name] = z
            return z

    def add_environment(self):
        if self._environment is not None:
            raise DataBuildingError('Environment zone already in Building')
        else:
            o = Zone('Environment')
            self._environment = o
            return o

    def del_environment(self):
        self._environment = None

    def del_zone(self, name):
        try:
            del self._zones[name]
        except KeyError:
            raise DataBuildingError('Zone %s not in Building' % name)

    def clean(self):
        self._zones = {}
        self._environment = None

class Zone(object):
    """Defines a thermal zone"""

    def __init__(self, name):
    
        self._name = name
        self._variables = {}
        #self.surfaces = {}

    @property
    def name(self):
        return self._name

    def get_variable(self, data_type, period):
        try:
            var = self._variables[data_type]
        except KeyError:
            raise DataZoneError('Variable %s not in Zone %s' % 
                (data_type, self._name))
        try:
            return var.get_values(period)
        except DataVariablePeriodError:
            raise DataZoneError('No %s data for %s in Zone %s' % 
                (period, data_type, self._name))

    def add_variable(self, data_type):

        if data_type in self._variables:
            raise DataZoneError('Variable %s already in Zone %s' % 
                (data_type, self._name))
        else:
            try:
                var = Variable(data_type)
            except DataVariableTypeError as e:
                raise DataZoneError(e)
            else:
                self._variables[data_type] = var
                return var
        
    def del_variable(self, data_type):

        try:
            del self._variables[data_type]
        except KeyError:
            raise DataZoneError('Variable %s not in Zone' % data_type)


# class Surface(object):
#     """Defines an enveloppe element through which heat is loss"""
# 
#     def __init__(self, name, surf, surf_type):
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
    pass

class DataVariablePeriodError(DataVariableError):
    pass

class DataVariableValueError(DataVariableError):
    pass

class DataBuildingError(DataError):
    pass

class DataZoneError(DataError):
    pass

