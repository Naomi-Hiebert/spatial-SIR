import matplotlib

# Ensure using PyQt5 backend
matplotlib.use("QT5Agg")

from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar, 
    FigureCanvasQTAgg as Canvas)


class MplCanvas(Canvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(
            self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        Canvas.updateGeometry(self)


class MplWidget(QtWidgets.QWidget):
    """Creates canvas on graphWidget, such that it can be plotted on. Inherits from QWidget
    Parameters
    ----------
    QtWidgets : PyQt Widget
        Allows canvas to be displayed on Widget.
    """

    def __init__(self, parent=None, toolbar=True):
        QtWidgets.QWidget.__init__(self, parent)  # Inherit from QWidget
        self.canvas = MplCanvas()  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()  # Set box for plotting
        if toolbar:
            bar = NavigationToolbar(self.canvas, self)
            self.vbl.addWidget(bar)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

    def plot(self, X=None, y=None, fmt='-', **kwargs):
        """Plots given X and y data to widget plot.
        Parameters
        ----------
        X : array-like or scalar
            Horizontal coordinates of data points.
        y : array-like or scalar
            Vertical coordinates of data points.
        """
        return self.canvas.ax.plot(X, y, fmt, **kwargs)
