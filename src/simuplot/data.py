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


class Array(object):
    """ Store numpy array and return values for time interval
        or perform calculation
    """
    
    def __init__(self, values):
        print 'ici !!!!!!!'
        self._vals = np.array(values)
    
    # Return initial array
    @property
    def vals(self):
        return self._vals
        
    # Return values for time interval
    def _get_interval(self, interval = None):
        if interval == None :
            return self._vals
        else :
            return None
        
    # Return sum over the desired periods
    def _sum_period(self, interval) :
        return None

    # Return average value over the desired periods
    def _avg_period(self, interval) :
        return None
        
    # Return typical days for desired periods
    def _typical_day(self, per=None, start=None, end=None):
        return None
        
    # Return values for period with pre-calculation
    def get_values(self, interval = None, precalc =None ):        
        # Extract interval and perform desired pre-calculation
        # If no pre-calculation required, return corresponding interval
        if precalc == None :
            out_array = self._get_interval(interval)
        
        elif precalc == 'sum' :
            out_array = self._sum_period(interval)
            
        elif precalc == 'average' :
            out_array = self._avg_period(interval)
            
        elif precalc == 'typical day' :
            out_array = self._typical_day(interval)
            
        return out_array

        

class Variable(object):
    """Stores Arrays objects for one physical parameter (temperature,
       heat demand,...
    """

    def __init__(self, data_type):
    
        # Data type
        if data_type not in DataTypes:
            raise DataVariableTypeError(self.tr(
                'Incorrect data type {}').format(data_type))
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

    def get_array(self, period):
        if period not in DataPeriods:
            raise DataVariablePeriodError(self.tr(
                'Incorrect sample period {}').format(period))
        try:
            return self._values[period]
        except KeyError:
            raise DataVariableNoValueError(self.tr(
                'No value for sample period {}').format(period))

    def set_array_from_list(self, period, val_list):
        """Set val_list as values
            
            val_list: list of numbers in numeric or string format
        """
        if period not in DataPeriods:
            raise DataVariablePeriodError(self.tr(
                'Incorrect sample period {}').format(period))
        try:
            self._values[period] = Array(val_list)
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

    @property
    def zones(self):
        """Return zone names"""
        return self._zones.keys()

    def get_zone(self, name):
        try:
            return self._zones[name]
        except KeyError:
            raise DataBuildingError(self.tr(
                'Zone {} not in Building').format(name))

    def add_zone(self, name):
        if name in self._zones:
            raise DataBuildingError(self.tr(
                'Zone {} already in Building').format(name))
        else:
            z = Zone(name)
            self._zones[name] = z
            return z

    def del_zone(self, name):
        try:
            del self._zones[name]
        except KeyError:
            raise DataBuildingError(self.tr(
                'Zone {} not in Building').format(name))

    def get_environment(self):
        return self._environment

    def add_environment(self):
        if self._environment is not None:
            raise DataBuildingError(self.tr(
                'Environment zone already in Building'))
        else:
            o = Zone(self.tr('Environment'))
            self._environment = o
            return o

    def del_environment(self):
        self._environment = None

    def clean(self):
        self._zones = {}
        self._environment = None

class Zone(object):
    """Define a thermal zone
    
       Public attributes:
       - name (str): name of the Zone
       - variables (str list): variable types available for the Zone

       Public methods:
       - get_variable_periods
       - get_values
       - set_values_from_list
       """

    def __init__(self, name):
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
                'Variable {} not in Zone {}').format(data_type, self._name))

    def _add_variable(self, data_type):
        """Add variable of type data_type"""
        if data_type in self._variables:
            raise DataZoneError(self.tr(
                'Variable {} already in Zone {}').format(data_type, self._name))
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
                'Variable {} not in Zone {}').format(data_type, self._name))

    def get_variable_periods(self, data_type):
        """Return list of available periods for type data_type"""
        self._get_variable(data_type).periods

    def get_values(self, data_type, period, interval = None, precalc = None):
        """Return values of variable of type data_type for period"""
        try:
            var = self._variables[data_type]
        except KeyError:
            raise DataZoneError(self.tr(
                'Variable {} not in Zone {}').format(data_type, self._name))
        try:
            array = var.get_array(period)
            return array.get_values(interval, precalc)
        except DataVariablePeriodError as e:
            raise DataZoneError(e + self.tr('while getting values for {} '
                'in Zone {}').format(data_type, self._name))
        except DataVariableNoValueError:
            raise DataZoneError(self.tr('No {} data for {} '
                'in Zone {}').format(period, data_type, self._name))

    def set_values_from_list(self, data_type, period, val_list):
        """Set values of variable of type data_type for period
        
            data_type (str): data type
            period (str): period
            val_list (list): list of numbers in numeric or string format
            """
        if data_type in self.variables:
            var = self._variables[data_type]
        else:
            var = self._add_variable(data_type)
        
        try:
            var.set_array_from_list(period, val_list)
        except DataVariablePeriodError as e:
            raise DataZoneError(str(e) 
                                + self.tr(' while setting values for {} '
                                'in Zone {}').format(data_type, self._name))
        except DataVariableValueError as e:
            raise DataZoneError(str(e) 
                                + self.tr(' while setting values for {} '
                                'in Zone {}').format(data_type, self._name))

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
    """Data type does not exist"""
    pass

class DataVariablePeriodError(DataVariableError):
    """Data sample period does not exist"""
    pass

class DataVariableValueError(DataVariableError):
    """Value is of wrong type"""
    pass

class DataVariableNoValueError(DataVariableError):
    """Requested value is not available"""
    pass

class DataBuildingError(DataError):
    pass

class DataZoneError(DataError):
    pass

