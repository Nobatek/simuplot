# -*- coding: utf-8 -*-

# List all plotter widget classes

# To add a new plotter, add a .py file to the dataplotter directory
# and add it to the list. The order of the list matters. It is the order
# of the tabs to be created.

# Each plotter should have 
# - a "name" attribute
# - a "refresh data" slot

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from .consperzonepie import ConsPerZonePie
from .thermalcomfhistog import ThermalComfHistog
from .heatgainpie import HeatGainPie
from .periodicplot import PeriodicPlot
from .pilebargainloss import PileBarGainLoss
from .neubrager import NEUBrager

plotters = [
    ConsPerZonePie,
    ThermalComfHistog,
    HeatGainPie,
    PeriodicPlot,
    PileBarGainLoss,
    NEUBrager,
]

