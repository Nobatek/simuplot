# -*- coding: utf-8 -*-

from PyQt4 import QtGui

from matplotlib.figure import Figure

from matplotlib.backends.backend_qt4agg \
    import FigureCanvasQTAgg as FigureCanvas

from matplotlib.backends.backend_qt4agg \
    import NavigationToolbar2QT as NavigationToolbar 

class MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self):
        
        # Setup Matplotlib Figure and Axis
        self.fig = Figure(facecolor="white")
        self.axes = self.fig.add_subplot(111)

        # Initialization of the canvas
        super(MplCanvas, self).__init__(self.fig)

        # Define the widget as expandable
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)

        # Notify the system of updated policy
        FigureCanvas.updateGeometry(self)
    
class MplWidget(QtGui.QWidget):
    """Widget defined in Qt Designer"""
    def __init__(self, parent = None):
        
        super(MplWidget, self).__init__(parent)

        # Set canvas and navigation toolbar
        self.canvas = MplCanvas()
        self.ntb = NavigationToolbar(self.canvas, self)

        # Layout as vertical box
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.vbl.addWidget(self.ntb)
        self.setLayout(self.vbl)

