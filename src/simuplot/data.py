# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import string
import datetime as dt
import numpy as np

from PyQt4 import QtCore
from PyQt4.QtCore import QT_TRANSLATE_NOOP as translate

from simuplot import SimuplotError

DATATYPES = {
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

DATAPERIODS = [
    'HOUR',
    'DAY',
    'MONTH',
    'YEAR',
]

# TODO: translate short names as well
MONTHS = [
    ('Jan', 31, ['01/01', '01/31'], (translate('Data', 'January'))),
    ('Fev', 28, ['02/01', '02/28'], (translate('Data', 'February'))),
    ('Mar', 31, ['03/01', '03/31'], (translate('Data', 'March'))),
    ('Apr', 30, ['04/01', '04/30'], (translate('Data', 'April'))),
    ('May', 31, ['05/01', '05/31'], (translate('Data', 'May'))),
    ('Jun', 30, ['06/01', '06/30'], (translate('Data', 'June'))),
    ('Jul', 31, ['07/01', '07/31'], (translate('Data', 'July'))),
    ('Aug', 31, ['08/01', '08/31'], (translate('Data', 'August'))),
    ('Sep', 30, ['09/01', '09/30'], (translate('Data', 'September'))),
    ('Oct', 31, ['10/01', '10/31'], (translate('Data', 'October'))),
    ('Nov', 30, ['11/01', '11/30'], (translate('Data', 'November'))),
    ('Dec', 31, ['12/01', '12/31'], (translate('Data', 'December'))),
]

# TODO: move to user settings
SEASONS = [(translate('Data', 'Year'), ['01/01', '12/31']),
           (translate('Data', 'Summer'), ['04/01', '09/30']),
           (translate('Data', 'Winter'), ['10/01', '03/31']),
          ]

def date2dt(date):
    """Returns a datetime corresponding to date

       date: date as a string of the form 'MM/dd'
       e.g.: date2dt('31/12')
    """

    try:
        [month, day] = string.split(date, '/')
        return dt.datetime(2005, int(month), int(day), 0, 0, 0)
    except (TypeError, ValueError):
        raise DataDateError(translate('Data', 'Invalid date: {}').format(date))

class TimeInterval(QtCore.QObject):
    """A TimeInterval is defined by a list containing two boundaries
       if the first boundary is greater than the second, the time interval
       be slitted. The boundaries must be date times object and its not
       necessary to specify hour or year info
       input :
      [begin_interval1, end_interval1]
    """

    def __init__(self, beg_dt, next_dt):

        super(TimeInterval, self).__init__()

        # TODO: check datetime is 2005 or 01/01/2006 ?
        # If beg_dt = next_dt, a whole wrapped year is returned

        if beg_dt < next_dt:
            self._intervals = [[beg_dt, next_dt]]
        else:
            day0_dt = dt.datetime(2005, 1, 1, 0, 0, 0)
            day365_dt = dt.datetime(2006, 1, 1, 0, 0, 0)
            self._intervals = [[day0_dt, next_dt],
                               [beg_dt, day365_dt]]

    @classmethod
    def from_strings(cls, beg, end):
        return cls(date2dt(beg),
                   date2dt(end) + dt.timedelta(days=1))

    @classmethod
    def from_string_seq(cls, beg_end):
        return cls.from_strings(beg_end[0], beg_end[1])

    @classmethod
    def from_month_nb(cls, month_nb):
        # month_nb is in range(0,12)
        try:
            return cls.from_string_seq(MONTHS[month_nb][2])
        except IndexError:
            raise DataDateError(translate(
                'Data', 'Invalid month number: {}').format(month_nb))

    def get_dt_interval_list(self):
        return self._intervals

    def get_indexes(self, period):
        if period not in DATAPERIODS:
            raise DataTimeIntervalPeriodError(self.tr(
                'Incorrect sample period {}').format(period))

        def dt2index(date_dt, period):
            if period == 'HOUR':
                return(date_dt - dt.datetime(2005, 1, 1, 0, 0, 0)).days * 24
            elif period == 'DAY':
                return(date_dt - dt.datetime(2005, 1, 1, 0, 0, 0)).days
            else:
                raise NotImplementedError

        return np.concatenate([np.arange(dt2index(beg, period),
                                         dt2index(end, period))
                               for beg, end in self._intervals])

    def get_dt_range(self, period):
        if period not in DATAPERIODS:
            raise DataTimeIntervalPeriodError(self.tr(
                'Incorrect sample period {}').format(period))

        if period == 'HOUR':
            def dt_range(beg, end):
                return [beg + dt.timedelta(hours=i)
                        for i in range((end - beg).days * 24)]
        elif period == 'DAY':
            def dt_range(beg, end):
                return [beg + dt.timedelta(days=i)
                        for i in range((end - beg).days)]
        else:
            raise NotImplementedError

        return np.concatenate([dt_range(beg, end)
                               for beg, end in self._intervals])

class Array(QtCore.QObject):
    """ Store numpy array and return values for time interval
        or perform calculation
    """

    def __init__(self, values, period):

        super(Array, self).__init__()

        self._values = np.array(values)
        self._period = period

    def apply(self, function):
        """Apply function to array of values"""
        self._values = function(self._values)

    def values(self, t_interval=None):
        """Return a np.array containing the array values

           If optional TimeInterval is specified, the returned array
           contains a subset corresponding to the TimeInterval.
        """
        if t_interval is None:
            return self._values
        else:
            try:
                return self._values[t_interval.get_indexes(self._period)]
            except IndexError:
                raise DataArrayIndexError()

    def sum(self, t_interval=None):
        """Return sum over the desired interval"""
        return self.values(t_interval).sum()

    def mean(self, t_interval=None):
        """Return mean value over the desired interval"""
        return np.mean(self.values(t_interval))

    def typical_day(self, t_interval=None):
        """Return typical days for desired interval"""
        # TODO: implement Array.typical_day
        raise NotImplementedError

class Variable(QtCore.QObject):
    """Stores an array of values for one physical parameter (temperature,
       heat demand,...)
    """

    def __init__(self, data_type):

        super(Variable, self).__init__()

        # Data type
        if data_type not in DATATYPES:
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
        if period not in DATAPERIODS:
            raise DataVariablePeriodError(self.tr(
                'Incorrect sample period {}').format(period))
        try:
            return self._values[period]
        except KeyError:
            raise DataVariableNoValueError(self.tr(
                'No value for sample period {}').format(period))

    def set_array(self, period, array):
        if period not in DATAPERIODS:
            raise DataVariablePeriodError(self.tr(
                'Incorrect sample period {}').format(period))

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
                'Zone {} not in Building').format(name))

    def add_zone(self, name):
        if name in self._zones:
            raise DataBuildingError(self.tr(
                'Zone {} already in Building').format(name))
        else:
            zone = Zone(name)
            self._zones[name] = zone
            return zone

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
            env = Zone(self.tr('Environment'))
            self._environment = env
            return env

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
       - get_array
       - set_array
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
        return self._get_variable(data_type).periods

    def get_array(self, data_type, period):
        """Return Array of variable of type data_type for period"""
        try:
            var = self._variables[data_type]
        except KeyError:
            raise DataZoneError(self.tr(
                'Variable {} not in Zone {}'
                ).format(data_type, self._name))
        try:
            return var.get_array(period)
        except DataVariablePeriodError as e:
            raise DataZoneError(self.tr(
                '{} while getting values for {} in Zone {}'
                ).format(e, data_type, self._name))
        except DataVariableNoValueError:
            raise DataZoneError(self.tr(
                'No {} data for {} in Zone {}'
                ).format(period, data_type, self._name))

    def set_array(self, data_type, period, array):
        """Set Array of variable of type data_type for period

            data_type (unicode): data type
            period (unicode): period
            array (Array): array of values
            """
        if data_type in self.variables:
            var = self._variables[data_type]
        else:
            var = self._add_variable(data_type)

        try:
            var.set_array(period, array)
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

class DataDateError(DataError):
    pass

class DataTimeIntervalError(DataError):
    pass

class DataTimeIntervalPeriodError(DataTimeIntervalError):
    pass

class DataArrayError(DataError):
    pass

class DataArrayIndexError(DataArrayError):
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

