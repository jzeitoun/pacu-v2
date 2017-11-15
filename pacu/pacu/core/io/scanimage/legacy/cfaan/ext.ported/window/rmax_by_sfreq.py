from PyQt4.QtCore import QRect, Qt
from pyqtgraph import GraphicsWindow, LabelItem, mkPen
from ext.console import debug
from parse_tuning import Response

class RMaxBySpatialFrequencyFig(GraphicsWindow):
    def __init__(self):
        super(RMaxBySpatialFrequencyFig, self).__init__()
        self.setWindowTitle('Spatial Frequency Tunig Curve')
        self.setGeometry(QRect(686, 33, 296, 296))
        plotItem = self.addPlot()
        plotItem.setLabels(left='rmax', bottom='spatial frequency')
        self.rawPlotDataItem = plotItem.plot([], [], pen='k', symbol='o', symbolPen='k', symbolSize=6, symbolBrush=None, antialias=True)
        self.fitPlotDataItem = plotItem.plot([], [], pen=mkPen('k', width=1, style=Qt.DashLine), antialias=True)

#         sidePlotItem = self.addPlot()
#         self.sidePlotDataItem = sidePlotItem.plot([], [], pen='k', symbol='o', symbolPen='k', symbolSize=6, symbolBrush=None, antialias=True)

    def updatePlot(self, trace, conditions, freq_meta):
        rmax_by_sfreq = Response.rmax_by_sfreq(trace, conditions, freq_meta)
        self.rawPlotDataItem.setData(*zip(*rmax_by_sfreq))
