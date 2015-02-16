import os

# Create a list of all plotter widget classes

# To add a new plotter, just add a .py file to the dataplotter directory
# The plotter class should be called Plotter and have 
# - a "name" attribute
# - a "refresh data" slot

plotters = []
for filename in os.listdir(os.path.dirname(__file__)):
    if filename[-3:] == '.py':
        if filename != '__init__.py' and filename != 'dataplotter.py':
            plotters.append(__import__(filename[:-3], locals(), globals()).Plotter)

del os

