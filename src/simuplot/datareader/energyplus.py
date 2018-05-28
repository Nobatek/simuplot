import os

import csv
import re

from PyQt5 import QtGui, QtWidgets

from simuplot.data import Array
from .datareader import DataReader, DataReaderReadError

class EnergyPlus(DataReader):
    """Reads Energy Plus data files"""

    # Data type translations
    # TODO: Complete. Externalize in some config file ?
    DataTypes = {
        # Climate
        'Outdoor Air Drybulb Temperature':
            'AIR_DRYBULB_TEMPERATURE',
        'Outdoor Air Wetbulb Temperature':
            'AIR_WETBULB_TEMPERATURE',
        'Outdoor Air Humidity Ratio':
            'AIR_HUMIDITY_RATIO',
        'Diffuse Solar Radiation Rate per Area':
            'DIFFUSE_SOLAR_RADIATION',
        'Direct Solar Radiation Rate per Area':
            'DIRECT_SOLAR_RADIATION',
        # Zone
        'Mean Air Temperature':
            'AIR_DRYBULB_TEMPERATURE',
        'Mean Air Humidity Ratio':
            'AIR_HUMIDITY_RATIO',
        'Operative Temperature':
            'OPERATIVE_TEMPERATURE',
        # Zone loads
        'Ideal Loads Supply Air Total Heating Rate':
            'HEATING_RATE',
        'Ideal Loads Supply Air Total Cooling Rate':
            'COOLING_RATE',
        # Zone behaviour
        'People Occupant Count':
            'PEOPLE_COUNT',
        # Zone heat gains
        'People Total Heating Rate':
            'PEOPLE_HEATING_RATE',
        'Lights Total Heating Rate':
            'LIGHTING_HEATING_RATE',
        # TODO: Gas, Hot Water, Steam, Other Equipment
        'Electric Equipment Total Heating Rate':
            'EQUIPMENT_HEATING_RATE',
        'Windows Total Heat Gain Rate':
            'WINDOWS_HEATING_RATE',
        'Opaque Surface Inside Faces Total Conduction Heat Gain Rate':
            'OPAQUE_SURFACES_HEATING_RATE',
        'Infiltration Total Heat Gain Energy':
            'INFILTRATION_HEATING_RATE',
    }
    # Unit translations
    DataUnits = {
        '':'',
        'C':'°C',
        'W':'W',
        'kgWater/kgDryAir':'%',
        'W/m2':'W/m2',
        'J':'J',
    }

    # Sampling period conversion
    # TODO: Complete. Externalize in some config file ?
    # TODO: Manage RunPeriod. Currently breaks input filter.
    DataPeriods = {
        'Hourly':'HOUR',
    }

    # Strings to remove from item names in column headers
    # Watch the trailing/leading spaces
    strings_to_remove = [' IDEAL LOADS AIR',
                         'PEOPLE ',
                        ]

    def __init__(self, building):

        super(EnergyPlus, self).__init__(building)

        self._name = 'Energy Plus'

        # Connect browse and load buttons
        self.filePathBrowseButton.clicked.connect(self.browse_button_cbk)
        self.filePathButtonBox.accepted.connect(self.load_button_cbk)

    @property
    def name(self):
        return self._name

    def browse_button_cbk(self):
        """Browse button callback"""

        # Launch file selection dialog, get file path,
        # and print it in file path text widget
        file_path = QtWidgets.QFileDialog.getOpenFileName()[0]
        if file_path != '':
            self.filePathEdit.setText(file_path)

    def load_button_cbk(self):
        """Load button callback"""

        # Get file path from filePathEdit
        file_path = self.filePathEdit.text()

        # Initialize progress bar
        self.dataLoadProgress.emit(0)

        # Clean Building
        self._building.clean()

        # Read file
        self.loadingData.emit(file_path)
        try:
            messages = self.read_data_files(file_path)
        except DataReaderReadError as e:
            # Error reading file. Clean Building and signal error.
            self._building.clean()
            self.dataLoadError.emit(self.tr("[Error] {}").format(e))
        else:
            # Signal data was loaded
            # Return last message in queue
            self.dataLoaded.emit(messages[-1])

    def read_data_files(self, file_path):

        messages = ['']

        # Count total number of data lines (excluding header) to show progress
        with open(file_path, 'r') as f:
            nb_lines = sum(1 for line in f) - 1

        # Open file
        try:
            csv_file = open(file_path, "r")
        except IOError:
            raise DataReaderReadError(self.tr(
                "Wrong filepath: {}").format(file_path))
        except UnicodeDecodeError:
            raise DataReaderReadError(self.tr(
                "Unauthorized characters in data file"))

        # Create CSV reader, store file size to track progress while reading
        csv_reader = csv.reader(csv_file, delimiter=',')
        file_size = os.path.getsize(file_path)

        # Except for the first ('Date/Time'),
        # each column head should be of the form
        # ZONE_NAME:Variable Name [Unit](Periodicity)
        # Use a regular expression pattern to match column heads
        # Warning: this regexp is broken by files with "DistrictHeating"
        pattern = re.compile(r"""
            (?P<item_name>.*)       # Item name
            :                       # Colon
            (?P<item_type>[^ ]*)    # Item type (Zone, Site, etc)
            \                       # 1 whitespace
            (?P<var>.*?)            # Var name
            \ \[                    # 1 whitespace, opening square bracket
            (?P<unit>.*?)           # Var unit
            \]\(                    # Closing square bracket, opening parenthese
            (?P<period>.*?)         # Var periodicity
            \)                      # Closing parenthese
            .*""", re.VERBOSE)

        # Initialize empty variable list
        variables = []
        # Variables store data as numpy arrays. Those can't be appended.
        # During the reading, store data in simple lists.
        tmp_variables = []

        # Get header line
        header = list(next(csv_reader))

        # Remove first column header ('Date/Time')
        # Incidentally check the file is an E+ file
        try:
            header.remove('Date/Time')
        except ValueError:
            raise DataReaderReadError(self.tr(
                "Invalid file header: '{},...', E+ file begins with 'Date/Time'"
                ).format(header[0]))

        # Go through all columns heads
        for head in header:
            # Match colum head to extract values
            try:
                match = pattern.match(head)
                # E+ replaces '_' with '%' in zone names. We want our '_' back.
                item_name_str = match.group('item_name').replace('%', '_')
                item_type_str = match.group('item_type')
                var_str = match.group('var')
                unit_str = match.group('unit')
                period_str = match.group('period')

            except AttributeError:
                raise DataReaderReadError(self.tr(
                    'Misformed column head: "{}"').format(head))

            # Remove unwanted strings from name
            for s in self.strings_to_remove:
                item_name_str = item_name_str.replace(s, '')

            # Get data type from E+ column header name
            try:
                data_type = self.DataTypes[var_str]
            except KeyError:
                # We don't know that type. Ignore that column.
                variables.append([None, None, None, None])
                tmp_variables.append(None)
                messages.append(self.tr(
                    '[Warning] Unknown data type: {}').format(var_str))
                continue

            # Get data unit from E+ column header name
            try:
                data_unit = self.DataUnits[unit_str]
            except KeyError:
                # We don't know that unit. Ignore that column.
                variables.append([None, None, None, None])
                tmp_variables.append(None)
                messages.append(self.tr(
                    '[Warning] Unknown unit: [{}]').format(unit_str))
                continue

            # If data type and unit are known, check item type
            if item_type_str == 'Zone':

                # Create zone if needed
                if item_name_str in self._building.zones:
                    item = self._building.get_zone(item_name_str)
                else:
                    item = self._building.add_zone(item_name_str)

            elif item_type_str == 'Site':

                if item_name_str == 'Environment':

                    # Create environment "zone" if needed
                    item = self._building.get_environment()
                    if item is None:
                        item = self._building.add_environment()
                else:
                    # What ?
                    item = None

            elif item_type_str == 'Surface':
                # Ignore for now
                item = None

            else:
                # What ?
                item = None

            # Translate E+ period into DataPeriod
            try:
                period = self.DataPeriods[period_str]
            except KeyError:
                raise DataReaderReadError(self.tr(
                    'Unknown period {}').format(period_str))

            # Store locally in variable list (one var per column)
            # before final insertion into Variable as a numpy array
            variables.append([item, data_type, data_unit, period])
            tmp_variables.append([])

        # Go through all lines to store values in each variable
        nb_values_per_line = len(variables)

        for line_nb, row in enumerate(csv_reader):

            # Skip first column ('Date/Time')
            vals = row[1:]

            # Ignore empty line ("It's alright, no big deal")
            if vals == []:
                continue

            # Check correct number of values in the line
            # This is broken if file contains "DistrictHeating"
            if len(vals) != nb_values_per_line:
                raise DataReaderReadError(self.tr(
                    'Misformed line: {}').format(row))

            # Store each value of known type in the line into its list
            try:
                for i, val_list in enumerate(tmp_variables):
                    if val_list is not None:
                        val_list.append(float(vals[i]))
            except ValueError:
                raise DataReaderReadError(self.tr(
                    'Invalid value in line: {}').format(row))

            # Update progress bar
            self.dataLoadProgress.emit(100 * (line_nb + 1) / nb_lines)

        csv_file.close()

        # Store all temporary value lists into numpy arrays in item variables
        for i, [item, data_type, data_unit, per] in enumerate(variables):
            if item is not None:
                # Unit conversion
                try:
                    conv_func = self.conversions[data_type][data_unit]
                except KeyError:
                    messages.append(self.tr(
                        '[Warning] Unexpected unit [{}] for data type {}'
                        ).format(data_unit, data_type))
                    continue
                data_array = Array(tmp_variables[i], per)
                data_array.apply(conv_func)
                # TODO: check there is not data already
                # for this type and period in this zone ?
                item.set_array(data_type, per, data_array)

        return messages

