# -*- coding: utf-8 -*-

from __future__ import division

from PyQt4 import QtCore, QtGui

import numpy as np

import matplotlib.pyplot as plt

from .dataplotter import DataPlotter, DataPlotterError

from data import DataZoneError

# TODO: This module is broken if start date is not January 1st
# The simulation length must be one year, and the period 'HOUR'
# Should this be made more generic ?
periods = {'Annual' : [[0,8760]],
           'Summer' : [[2879,6553]],
           'Winter' : [[0,2779],[6553,8760]],
           }