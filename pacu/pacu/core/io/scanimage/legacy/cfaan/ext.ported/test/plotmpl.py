import numpy as np

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt4 import QtGui, QtCore
from ext.console import debug

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                    QtGui.QSizePolicy.Expanding,
                                    QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def compute_initial_figure(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)
        self.axes.plot(t, s)


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l = [np.random.randint(0, 10) for i in range(4)]
        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.draw()

main_widget = QtGui.QWidget()
l = QtGui.QVBoxLayout(main_widget)
sc = MyStaticMplCanvas(main_widget, width=5, height=4, dpi=100)
dc = MyDynamicMplCanvas(main_widget, width=5, height=4, dpi=100)
l.addWidget(sc)
l.addWidget(dc)
main_widget.show()
main_widget.move(0, 0)

# w.setWindowTitle('Simple')
# w.show()

# gw = GraphicsWindow()
# gw.move(0, 0)
# gw.show()
# 
# plotItem = gw.addPlot(title='Timed data',
#         axisItems={'bottom': TimeAxisItem(orientation='bottom')})
# 
# plotItem.setLabels(left='rmax', bottom='spatial frequency')
# bitem = plotItem.axes['bottom']['item']
# ticks = bitem.tickValues(0, 100, 4)
# bitem.setTicks([
#     [(1,1), (2,2), (4,4), (7,7)],
#     [(3,3), (2,2), (4,4), (7,7)],
# ])
# debug.enter()
# plotItem.plot([1,2,3], [1,2,3],
#         pen='k', symbol='o', symbolPen='k',
#         symbolSize=6, symbolBrush=None, antialias=True)

# rawPlotDataItem = plotItem.plot([], [],
#         pen='k', symbol='o', symbolPen='k',
#         symbolSize=6, symbolBrush=None, antialias=True)
# fitPlotDataItem = plotItem.plot([], [],
#         pen=mkPen('k', width=1, style=Qt.DashLine), antialias=True)
