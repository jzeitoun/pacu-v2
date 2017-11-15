import numpy as np

from PyQt4.QtCore import QPointF
from PyQt4.QtGui import QPolygonF, QGraphicsPolygonItem
from pyqtgraph import PolyLineROI, LinearRegionItem, mkPen

from ext.console import debug
from ext.util.calc.centroid import ExternalDivision

class OuterROI(QGraphicsPolygonItem):
    def __init__(self):
        super(OuterROI, self).__init__()
    @classmethod
    def new(cls, inner, positions):
        self = cls()
        self.inner = inner
        self.positions = positions
        self.main = self.inner.tiffFig.parent()
        self.setPen(mkPen(color='c', width=1))
        self.set_poly_from_pos(positions)
        return self

    def set_poly_from_pos(self, positions, isactive=True, m=2, n=1):
        if isactive:
            # positions = ExternalDivision(positions).get_3rd_points_by(1).round().astype(int)
            positions = ExternalDivision(positions).get_3rd_points_by_ratio(m=m, n=n).round().astype(int)
            polygon = QPolygonF(map(QPointF, *positions.T))
        else:
            polygon = QPolygonF()
        self.setPolygon(polygon)
    def inner_will_delete(self):
        self.inner = None
        self.positions = None
        self.main = None
    def inner_will_append_view(self, view):
        view.addItem(self)
    def inner_did_change_region(self, option):
        points = self.inner.getPoints()
        self.set_poly_from_pos(np.array(points), option.active, option.m, option.n)
    def neuropil_option_changed(self, option):
        points = self.inner.getPoints()
        self.set_poly_from_pos(np.array(points), option.active, option.m, option.n)
        # self.set_poly_from_pos(self.positions, option.active, option.m, option.n)
        # debug.enter()
        # self.inner.update_responsefig()
        # if self.inner.tiffFig.roi_current:
        #     self.inner.tiffFig.roi_current.update_responsefig()

        # self.traceFig.update_gray_bars()
    def get_polygon(self):
        return self.polygon().toPolygon()

class OuterROIOption(object):
    m = None
    n = None
    active = None
    def __init__(self, m=2, n=1, active=True):
        self.m = m
        self.n = n
        self.active = active
