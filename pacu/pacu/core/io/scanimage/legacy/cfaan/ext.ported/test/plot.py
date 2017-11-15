import numpy as np

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QSizePolicy
from ext.console import debug

class MPLCanvas(FigureCanvas):
    def __init__(self, parent, *args, **kwargs):
        super(MPLCanvas, self).__init__(Figure())
        layout = QtGui.QVBoxLayout(parent)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.initialize(*args, **kwargs)
        self.updateGeometry()
    def initialize(self, *args, **kwargs):
        pass

class SimpleFigure(MPLCanvas):
    pass

# main_widget = QtGui.QWidget()
# main_widget.setWindowTitle('SF Tuning')
# main_widget.move(0, 0)
# main_widget.resize(300, 300)
# main_widget.show()
#
# sc = MPLCanvas(main_widget)
# axes = sc.figure.add_subplot(111)
# axes.set_title('SF Tuning')
# axes.hold(False)
# axes.plot(range(10), range(10))
# sc.figure.tight_layout()
# sc.draw()
# debug.enter()
