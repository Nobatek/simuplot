# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os

from PyQt4 import QtCore, QtGui

class StatusBar(QtGui.QStatusBar):

    def __init__(self):

        super(StatusBar, self).__init__()
        
        # TODO: Move progress bar to status bar
        
        # Create and add labels for normal and 
        # permanent indicators
        self._norm_indic = QtGui.QLabel()
        self._perm_indic = QtGui.QLabel()
        self.addWidget(self._norm_indic, 3)
        self.addPermanentWidget(self._perm_indic)
        
        # Create and hide progress bar
        self._progress_bar = QtGui.QProgressBar()
        self._progress_bar.hide()
        self.addWidget(self._progress_bar, 1)
    
        # On startup, no data is loaded
        self._set_data_loaded(False)

    def _set_data_loaded(self, status):
        """Toggle permanent indicator display"""
        if status:
            self._perm_indic.setText(self.tr('Data loaded'))
        else:
            self._perm_indic.setText(self.tr('No data loaded'))

    @QtCore.pyqtSlot(unicode)
    def dataLoaded(self, string):
        self._set_data_loaded(True)
        self._norm_indic.setText(string)
        self._progress_bar.hide()

    @QtCore.pyqtSlot(unicode)
    def dataLoadError(self, string):
        self._set_data_loaded(False)
        self._norm_indic.setText(string)
        self._progress_bar.hide()

    @QtCore.pyqtSlot(unicode)
    def loadingData(self, string):
        self._norm_indic.setText(self.tr(
            'Loading data file: {}').format(string))

    @QtCore.pyqtSlot(int)
    def dataLoadProgress(self, value):
        self._progress_bar.show()
        self._progress_bar.setValue(value)

    @QtCore.pyqtSlot(unicode)
    def warning(self, string):
        self._norm_indic.setText(string)

