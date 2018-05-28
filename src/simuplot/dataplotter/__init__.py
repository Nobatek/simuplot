# List all plotter widget classes

# To add a new plotter, add a .py file to the dataplotter directory
# and add it to the list. The order of the list matters. It is the order
# of the tabs to be created.

# Each plotter should have
# - a "name" attribute
# - a "refresh data" slot

from .heatdemandpie import HeatDemandPie
from .heatgainpie import HeatGainPie
from .heatgainpilebar import HeatGainPileBar
from .thermalcomforthistog import ThermalComfortHistog
from .adaptivecomfortscatter import AdaptiveComfortScatter
from .customplot import CustomPlot

PLOTTERS = [
    HeatDemandPie,
    HeatGainPie,
    HeatGainPileBar,
    ThermalComfortHistog,
    AdaptiveComfortScatter,
    CustomPlot,
]

