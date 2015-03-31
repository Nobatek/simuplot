# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import numpy as np

from datetime import datetime

from PyQt4 import QtCore

from PyQt4.QtCore import QT_TRANSLATE_NOOP as translate

from simuplot import SimuplotError


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


class TimeInterval(object):
    """A TimeInterval is defined by a list containing two boundaries
       if the first boundary is greater than the second, the time interval
       be slitted. The boundaries must be date times object and its not 
       necessary to specify hour or year info
       input :
      [begin_interval1, end_interval1]
    """
    
    def __init__(self, period) :
    
        # Set simulation first day (if Energyplus simulation it s a Sunday)
        # CAUTION : For now Simuplot works for full year only
        self._day0 = datetime(2005,1,1,0,0,0)
        self._day364 = datetime(2005,12,31,23,0,0)
        
        self._period = period
        
        # Set year for the boundaries
        self._period = [bound.replace(year = 2005) for bound in period ]
        
        # Set time and spilt the interval if necessary
        if period[1] < period[0] :
            # set the hour for beginning and ending days
            self._begin_date = self._period[1].replace(hour = 0)
            self._end_date = self._period[0].replace(hour = 23)
            
            # Create the interval list that defines the period
            self._period = [[self._begin_date, self._day364],
                            [self._day0, self._end_date]]
            
            # Create a list of delta object corresponding
            # to the time interval
            self._deltalist = [self._day364 - self._begin_date,
                               self._end_date - self._day0]
        else :
            # set the hour for beginning and ending days
            self._begin_date = self._period[0].replace(hour = 0)
            self._end_date = self._period[1].replace(hour = 23)
            
            # Store the interval list that defines the period
            self._period = [[self._begin_date, self._end_date]]
            
            # Create a list of delta object corresponding
            # to the time interval
            self._deltalist = [self._end_date - self._begin_date]
    
    @property
    def begin_date(self) :
        return self._begin_date
    
    @property
    def end_date(self) :
        return self._end_date
        
    def get_deltalist(self) :
        return self._deltalist
        
    def datetime_interval(self):
        return self._period

    # Return interval with relative hours boundary values
    def hours_interval(self):
        # TODO: create the interval for other periods
        # transform interval boundaries into delta values 
        # (relative to the first day of the year)
        hours_interval = [[bound - self._day0 
                          for bound in interval]
                          for interval in self._period]

        # convert timedelta into hour
        return [[bound.days * 24 + bound.seconds / 3600
                        for bound in interval]
                        for interval in hours_interval]
                


class Array(object):
    """ Store numpy array and return values for time interval
        or perform calculation
    """
    
    def __init__(self, values, period):
        self._vals = np.array(values)
        self._period = period        
    
    # Return initial array
    @property
    def vals(self):
        return self._vals
        
    # Return values for time interval
    def get_interval(self, interval = None):
        # Give a TimeInterval in argument
        # If no interval is specified
        # Return full year
        if interval == None :
            return self._vals
        else :
            # get hour interval from time interval
            period = interval.hours_interval()
            # gather the values for each interval in res array
            res = np.array([])
            for int in period :
                res = np.concatenate((res,self._vals[int[0]:int[1]]),axis=0)
            return res
        
    # Return sum over the desired interval
    def sum_interval(self, interval = None) :
        # If no interval is specified
        # Return sum value for full year
        if interval == None :
            return sum(self._vals)
        else :
            return sum(get_interval(interval))

    # Return mean value over the desired interval
    def mean_interval(self, interval) :
        # If no interval is specified
        # Return mean value for full year
        if interval == None :
            return mean(get_interval(interval))
        else :
            return mean(get_interval(interval))
        
    # Return typical days for desired interval
    def typical_day(self, per=None, start=None, end=None):
        return None        


        
class Variable(QtCore.QObject):
    """Stores an array of values for one physical parameter (temperature,
       heat demand,...)
    """

    def __init__(self, data_type):
    
        super(Variable, self).__init__()

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
        
    def __unicode__(self):
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
            self._values[period] = Array(val_list, period)
        except ValueError as e:
            raise DataVariableValueError(e)

    
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

class Zone(QtCore.QObject):
    """Define a thermal zone
    
       Public attributes:
       - name (unicode): name of the Zone
       - variables (unicode list): variable types available for the Zone

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
                ).format(data_type, self._name))

    def _add_variable(self, data_type):
        """Add variable of type data_type"""
        if data_type in self._variables:
            raise DataZoneError(self.tr(
                'Variable {} already in Zone {}'
                ).format(data_type, self._name))
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
                ).format(data_type, self._name))

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
                ).format(data_type, self._name))
        try:
            array = var.get_array(period)
            return array
        except DataVariablePeriodError as e:
            raise DataZoneError(self.tr(
                '{} while getting values for {} in Zone {}'
                ).format(e, data_type, self._name))
        except DataVariableNoValueError:
            raise DataZoneError(self.tr(
                'No {} data for {} in Zone {}'
                ).format(period, data_type, self._name))

    def set_values(self, data_type, period, val_list):
        """Set values of variable of type data_type for period
        
            data_type (unicode): data type
            period (unicode): period
            array (numpy array): array of values
            """
        if data_type in self.variables:
            var = self._variables[data_type]
        else:
            var = self._add_variable(data_type)
        
        try:
            var.set_array_from_list(period, val_list)

        except DataVariablePeriodError as e:
            raise DataZoneError(self.tr(
                '{} while setting values for {} in Zone {}'
                ).format(e, data_type, self._name))

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

class DataError(SimuplotError):
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

