# List all plotter widget classes

# To add a new plotter, add a .py file to the dataplotter directory
# and add it to the list. The order of the list matters. It is the order
# of the tabs to be created.

# Each plotter should have 
# - a "name" attribute
# - a "refresh data" slot

from consperzonepie import ConsPerZonePie
from thermalcomfhistog import ThermalComfHistog

plotters = [
    ConsPerZonePie,
    ThermalComfHistog,
]

