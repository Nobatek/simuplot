# -*- coding: utf-8 -*-

# List all reader widget classes

# To add a new reader, add a .py file to the datareader directory
# and add it to the list. The order of the list is the order in which 
# the readers will appear in the selection menu.

# Each reader should read one or several files (or get data from any 
# data source), store data into a Building (self._building), 
# then emit the "dataLoaded" signal.

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from .energyplus import EnergyPlus

readers = [
    EnergyPlus,
]

