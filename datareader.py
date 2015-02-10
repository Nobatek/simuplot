# -*- coding: utf-8 -*-

import csv

from PyQt4 import QtGui

# from data import Building

from data_tools import _translate, LectDat

class DataReader(object):
    """Virtual class

       Useless by itself. Implement in sub-clases
    """
    
    def __init__(self, file_path_text, info_load, progress_bar,
        browse_button, load_button):

        # Building isntance
        #self._building = None
        
        self._list_dat = None

        # Path to data file
        self._file_path = ''
        self._file_path_text = file_path_text
        self._info_load = info_load
        self._progress_bar = progress_bar

        # Connect browse and load buttons
        browse_button.clicked.connect(self.browse_button_cbk)
        load_button.clicked.connect(self.load_button_cbk)

    @property
    def list_dat(self):
        return self._list_dat

    def browse_button_cbk(self):
        """Browse button callback"""

        # Launch file selection dialog, get file path,
        # and print it in file path text widget
        self._file_path_text.setText(QtGui.QFileDialog.getOpenFileName())

    def load_button_cbk(self):
        """Load button callback"""
        
        # Instanciate a new Building
        #self._building = Building('My Building')

        # Get file path from File_Path_Text widget
        self._file_path = self._file_path_text.text()

        # Initialize progress bar
        self._progress_bar.setProperty("value", 0)

        # Read file
        self._list_dat = LectDat(self._file_path, self._progress_bar)
        
        # TODO: manage errors
        if isinstance(self._list_dat, list) :
            self._info_load.setText(_translate("Form","Fichier correctement charge ...", None))
        else :
            self._Info_Load.setText(_translate("Form", self._list_dat, None))

class EnergyPlusDataReader(DataReader):
    """Reads Energy Plus data files"""

    def __init__(self, *args):

        super(EnergyPlusDataReader, self).__init__(*args)

