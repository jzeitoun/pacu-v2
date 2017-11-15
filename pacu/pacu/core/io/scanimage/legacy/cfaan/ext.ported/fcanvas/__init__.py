from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QSizePolicy

class MPLCanvas(FigureCanvas):
    def __init__(self, parent, *args, **kwargs):
        super(MPLCanvas, self).__init__(Figure())
        if isinstance(parent, tuple) and len(parent) is 4:
            self.setGeometry(QtCore.QRect(*parent))
        else:
            layout = QtGui.QVBoxLayout(parent)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self)
            self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.initialize(*args, **kwargs)
        self.updateGeometry()
    def initialize(self, *args, **kwargs):
        pass
