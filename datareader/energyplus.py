# -*- coding: utf-8 -*-

import os

import csv
import re

from PyQt4 import QtCore, QtGui, uic

from datareader import DataReader, DataReaderReadError

class EnergyPlus(DataReader):
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
        'People Occupant Count':'PEOPLE_COUNT'
    }

    # Sampling period conversion
    # TODO: Complete. Externalize in some config file ?
    # TODO: Manage RunPeriod. Currently breaks input filter.
    DataPeriods = {
        'Hourly':'HOUR',
    }

    # Strings to remove from item names in column headers
    # Watch the trailing/leading spaces
    strings_to_remove = [' IDEAL LOAD',
                         'PEOPLE ',
                        ]

    # TODO: Convert into SI units
    # For now, we'll suppose data is provided in SI unit

    def __init__(self, building):

        super(EnergyPlus, self).__init__(building)
        
        self._name = 'Energy Plus'
        
        # Setup UI
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'energyplus.ui'),
                   self)
        
        # Path to data file
        self._file_path_text = self.File_Path_Text

        # Connect browse and load buttons
        self.Browse_Button.clicked.connect(self.browse_button_cbk)
        self.Ok_Load_Button.clicked.connect(self.load_button_cbk)

    @property
    def name(self):
        return self._name

    def browse_button_cbk(self):
        """Browse button callback"""

        # Launch file selection dialog, get file path,
        # and print it in file path text widget
        file_path = QtGui.QFileDialog.getOpenFileName()
        if file_path != '':
            self._file_path_text.setText(file_path)

    def load_button_cbk(self):
        """Load button callback"""
        
        # Get file path from File_Path_Text widget
        file_path = self._file_path_text.text()

        # Initialize progress bar
        self.dataLoadProgress.emit(0)

        # Clean Building
        self._building.clean()
        
        # Read file
        self.loadingData.emit(file_path)
        try:
            messages = self.read_data_files(file_path)
        except DataReaderReadError as e:
            # Error reading file. Clean Building and signal error.
            self._building.clean()
            self.dataLoadError.emit("[Error] %s" % e)
        else:
            # Signal data was loaded
            # Return last message in queue
            self.dataLoaded.emit(messages[-1])

    def read_data_files(self, file_path):

        messages = ['']
        
        # Open file
        try:
            csv_file = open(file_path, "rb")
        except IOError:
            raise DataReaderReadError("Wrong filepath: %s" % file_path)
        except UnicodeDecodeError:
            raise DataReaderReadError("Unauthorized characters in data file")
        
        # Create CSV reader, store file size to track progress while reading
        csv_reader = csv.reader(csv_file, delimiter=",")
        file_size = os.path.getsize(file_path)
        
        # Get header line
        header = next(csv_reader)
    
        # Except for the first ('Date/Time'), 
        # each column head should be of the form
        # ZONE_NAME:Variable Name [Unit](Periodicity)
        # Use a regular expression pattern to match column heads
        # Warning: this regexp is broken by files with "DistrictHeating"
        pattern = re.compile(r"""
            (?P<item_name>.*)?      # Item name
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
                # E+ replaces '_' with '%' in zone names. We want our '_' back.
                item_name_str = match.group('item_name').replace('%', '_')
                item_type_str = match.group('item_type')
                var_str = match.group('var')
                unit_str = match.group('unit')
                period_str = match.group('period')

                # Remove unwanted strings from name
                for s in self.strings_to_remove:
                    item_name_str = item_name_str.replace(s, '')

            except AttributeError:
                raise DataReaderReadError('Misformed column head: "%s"' % head)
            
            # Get data type from E+ column header name
            try:
                data_type = self.DataTypes[var_str]
				
            except KeyError:
                # We don't know that type. Ignore that column.
                variables.append([None, None])
                tmp_variables.append(None)
                messages.append("[Warning] Unknown data type: %s" % var_str)
                
            else:
                
                # If data type is known, check item type
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
                    raise DataReaderReadError('Unknown period %s' % period_str)
                
                # Store locally in variable list (one var per column)
                # before final insertion into Variable as a numpy array
                variables.append([item, data_type, period])
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

            # Update progress bar
            self.dataLoadProgress.emit(100 * csv_file.tell() / file_size)
        
        # Store all temporary value lists into numpy arrays in item variables
        for i, [item, data_type, per] in enumerate(variables):
            if item is not None:
                # TODO: check there is not data already 
                # for this type and period in this zone ?
                item.set_values_from_list(data_type, per, tmp_variables[i])

        return messages

