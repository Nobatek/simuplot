# Python Qt4 bindings for GUI objects
from PyQt4 import QtGui

# import the Qt4Agg FigureCanvas object, that binds Figure to
# Qt4Agg backend. It also inherits from QWidget

from matplotlib.backends.backend_qt4agg \
    import FigureCanvasQTAgg as FigureCanvas

from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QT as NavigationToolbar #import de la toolbar associee a la figure

# Matplotlib Figure object
import numpy as np
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self):
        # setup Matplotlib Figure and Axis
        self.fig = Figure(facecolor="white")
        self.axes = self.fig.add_subplot(111)
        
        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)

        # we define the widget as expandable
        FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)

        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)

    
    
class MplWidget(QtGui.QWidget):
    """Widget defined in Qt Designer"""
    def __init__(self, parent = None):
        # initialization of Qt MainWindow widget
        QtGui.QWidget.__init__(self, parent)
        self.mplwidget = QtGui.QWidget(self)
        
        # set the canvas to the Matplotlib widget
        self.canvas = MplCanvas()
        ntb = NavigationToolbar(self.canvas,self.mplwidget)

        # create a vertical box layout
        self.vbl = QtGui.QVBoxLayout()
        
        # add mpl widget to vertical box
        self.vbl.addWidget(self.canvas)
        self.vbl.addWidget(ntb)
        
        # set the layout to th vertical box
        self.setLayout(self.vbl)

    def MAJgraph(self):
        x = np.arange(0.0, 3.0, 0.01)
        y = np.cos(2*np.pi*x)
        self.canvas.axes.plot(x, y)
        self.canvas.draw()


    
