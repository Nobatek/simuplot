from PyQt5 import QtGui, QtWidgets

from matplotlib.figure import Figure

from matplotlib.backends.backend_qt4agg import (FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

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
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)

        # Notify the system of updated policy
        FigureCanvas.updateGeometry(self)

        # 'resize event' connection cid
        self.resize_cid = None

    def set_tight_layout_on_resize(self, value):
        """Set to True to let the layout adapt automatically on resize"""

        if value is True:
            self.resize_cid = self.mpl_connect(
                'resize_event', self.tight_layout)
            self.tight_layout()
        else:
            if self.resize_cid is not None:
                self.mpl_disconnect(self.resize_cid)
                self.resize_cid = None

    def tight_layout(self, event=None):
        """Call tight_layout on figure to auto-adapt the plot size"""
        try:
            self.fig.tight_layout()
        except ValueError as e:
            if str(e) == 'left cannot be >= right':
                pass
            else:
                raise

class MplWidget(QtWidgets.QWidget):
    """Widget defined in Qt Designer"""
    def __init__(self, parent=None):

        super(MplWidget, self).__init__(parent)

        # Set canvas and navigation toolbar
        self.canvas = MplCanvas()
        self.ntb = NavigationToolbar(self.canvas, self)

        # Layout as vertical box
        self.vbl = QtWidgets.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.vbl.addWidget(self.ntb)
        self.setLayout(self.vbl)

