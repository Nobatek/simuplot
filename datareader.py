# -*- coding: utf-8 -*-

import csv
import re

from PyQt4 import QtCore, QtGui

from data import Building, DataBuildingError

class DataReader(QtCore.QObject):
    
    # This signal is sent when data is successfully loaded
    # TODO: check what happens in case of load failure
    dataLoaded = QtCore.pyqtSignal()
    
    def __init__(self, building, file_path_text, info_load, progress_bar,
        browse_button, load_button):

        super(DataReader, self).__init__()
        
        # Building isntance
        self._building = building
        
        # Path to data file
        self._file_path = ''
        self._file_path_text = file_path_text
        self._info_load = info_load
        self._progress_bar = progress_bar

        # Connect browse and load buttons
        browse_button.clicked.connect(self.browse_button_cbk)
        load_button.clicked.connect(self.load_button_cbk)

    def browse_button_cbk(self):
        """Browse button callback"""

        # Launch file selection dialog, get file path,
        # and print it in file path text widget
        file_path = QtGui.QFileDialog.getOpenFileName()
        self._file_path_text.setText(file_path)

    def load_button_cbk(self):
        """Load button callback"""
        
        # Get file path from File_Path_Text widget
        self._file_path = self._file_path_text.text()

        # Initialize progress bar
        self._progress_bar.setProperty("value", 0)

        # Clean Building
        self._building.clean()
        
        # Read file
        try:
            self.read_data_files()
        except DataReaderReadError as e:
            # Error reading file. Log error and clean Building.
            self._info_load.setText("Error loading data file: %s" % e)
            self._building.clean()
        else:
            self._info_load.setText("Done loading data file")

        # Signal data was loaded
        self.dataLoaded.emit()

def read_data_files(self):
        raise NotImplementedError

class EnergyPlusDataReader(DataReader):
    """Reads Energy Plus data files"""

    # Variable type conversion
    # TODO: Complete. Externalize in some config file ?
    DataTypes = {
        'Outdoor Air Drybulb Temperature':'AIR_DRYBULB_TEMPERATURE',
        'Mean Air Temperature':'AIR_DRYBULB_TEMPERATURE',
        'Outdoor Air Wetbulb Temperature':'AIR_WETBULB_TEMPERATURE',
        'Outdoor Air Humidity Ratio':'AIR_HUMIDITY_RATIO',
        'Mean Air Humidity Ratio':'AIR_HUMIDITY_RATIO',
        'Operative Temperature':'OPERATIVE_TEMPERATURE',
        'Total Internal Total Heating Rate':'HEATING_RATE',
        'Diffuse Solar Radiation Rate per Area':'DIFFUSE_SOLAR_RADIATION',
        'Direct Solar Radiation Rate per Area':'DIRECT_SOLAR_RADIATION',
    }

    # Sampling period conversion
    # TODO: Complete. Externalize in some config file ?
    # TODO: Manage RunPeriod. Currently breaks input filter.
    DataPeriods = {
        'Hourly':'HOUR',
    }

    # TODO: Convert into SI units
    # For now, we'll suppose data is provided in SI unit

    def read_data_files(self):

        # TODO: What about file read errors ?
        # Log a warning ? launch dialog ? display error in status bar ?

        # Open file
        try:
            csv_file = open(self._file_path, "rb")
        except IOError:
            raise DataReaderReadError("Wrong filepath: %s" % self._file_path)
        except UnicodeDecodeError:
            raise DataReaderReadError("Unauthorized characters in data file")
        
        csv_reader = csv.reader(csv_file, delimiter=",")
        
        # Get header line
        header = next(csv_reader)
    
        # Except for the first ('Date/Time'), 
        # each column head should be of the form
        # ZONE_NAME:Variable Name [Unit](Periodicity)
        # Use a regular expression pattern to match column heads
        # Warning: this regexp is broken by files with "DistrictHeating"
        pattern = re.compile(r"""
            (?P<item_name>.*?)      # Item name
            :                       # Colon
            (?P<item_type>[^ ]*)    # Item type (Zone, Site, etc)
            \                       # 1 whitespace
            (?P<var>.*?)            # Var name
            \ \[                    # 1 whitespace, opening square bracket
            (?P<unit>.*?)           # Var unit
            \]\(                    # Closing square bracket, opening parenthese
            (?P<period>.*?)         # Var periodicity
            \)                      # Closing parenthese
            .*""", re.VERBOSE)
        
        # Initialize empty variable list
        variables = []
        # Variables store data as numpy arrays. Those can't be appended.
        # During the reading, store data in simple lists.
        tmp_variables = []
        
        # Remove first column header ('Date/Time')
        # Incidentally check the file is an E+ file
        try:
            header.remove('Date/Time')
        except ValueError :
            raise DataReaderReadError( \
                "Invalid file header: %s, E+ file begins with 'Date/Time'" 
                % header)
        
        # Go through all columns heads
        for head in header:
            # Match colum head to extract values
            try:
                match = pattern.match(head)
                item_name_str = match.group('item_name')
                item_type_str = match.group('item_type')
                var_str = match.group('var')
                unit_str = match.group('unit')
                period_str = match.group('period')
            except AttributeError:
                raise DataReaderReadError('Misformed column head: "%s"' % head)
            
            # Get data type from E+ column header name
            try:
                data_type = self.DataTypes[var_str]
            except KeyError:
                # We don't know that type. Ignore that column.
                variables.append([None, None])
                tmp_variables.append(None)
            else:
                
                # If data type is known, check item type
                if item_type_str == 'Zone':
                
                    # Create zone if needed
                    try:
                        zone = self._building.get_zone(item_name_str)
                    except DataBuildingError:
                        zone = self._building.add_zone(item_name_str)
                    
                    # Add variable to zone
                    # TODO: check variable already in zone (different period ?)
                    var = zone.add_variable(data_type)
                
                elif item_type_str == 'Site':
                    
                    if item_name_str == 'Environment':
                        
                        # Create environment "zone" if needed
                        env = self._building.get_environment()
                        if env is None:
                            env = self._building.add_environment()
                        
                        # Add variable to environment
                        var = env.add_variable(data_type)
                    else:
                        # What ?
                        var = None
                
                elif item_type_str == 'Surface':
                    # Ignore for now
                    var = None
                else:
                    # What ?
                    var = None

                # Translate E+ period into DataPeriod
                try:
                    period = self.DataPeriods[period_str]
                except KeyError:
                    raise DataReaderReadError('Unknown period %s' % period_str)
                
                # Store locally in variable list (one var per column)
                # before final insertion into Variable as a numpy array
                variables.append([var, period])
                tmp_variables.append([])
 
        # Go through all lines to store values in each variable
        nb_values_per_line = len(variables)
        
        for row in csv_reader:

            # Skip first column ('Date/Time')
            vals = row[1:]

            # Check correct number of values in the line
            # This is broken if file contains "DistrictHeating"
            if len(vals) != nb_values_per_line:
                raise DataReaderReadError("Misformed line: %s" % row)
                
            # Store each value of known type in the line into its list
            try:
                for i, val_list in enumerate(tmp_variables):
                    if val_list is not None:
                        val_list.append(float(vals[i]))
            except ValueError:
                raise DataReaderReadError("Invalid value in line: %s" % row)

        # Store all temporary value lists into numpy arrays in Variables
        for i, [var, per] in enumerate(variables):
            if var is not None:
                try:
                    var .set_values_from_list(per, tmp_variables[i])
                except DataVariableValueError:
                    # TODO: log a warning ? display error in status bar ?
                    pass

        # TODO: Make it actually progressive. Or remove it...
        self._progress_bar.setProperty("value", 100)

class DataReaderError(Exception):
    pass

class DataReaderReadError(DataReaderError):
    pass

