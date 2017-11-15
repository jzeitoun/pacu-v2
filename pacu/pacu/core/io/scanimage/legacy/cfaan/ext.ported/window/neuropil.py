from PyQt4.QtCore import QRect
from pyqtgraph import GraphicsWindow, LabelItem

class NeuropilMaskFig(GraphicsWindow):
    def __init__(self):
        super(NeuropilMaskFig, self).__init__()
        self.setWindowTitle('Neuropil Mask')
        self.setGeometry(QRect(686, 33, 296, 296))
        label = LabelItem(justify='right')
        self.addItem(label)
        # self.show(imageData)
        # self.p1 = self.addPlot(row=1, col=0)
        # self.p2 = self.addPlot(row=2, col=0)
        # self.region = pg.LinearRegionItem()         # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this item when doing auto-range calculations.
        # self.region.setZValue(10)
        # self.region.sigRegionChanged.connect(self.update)
        # self.p1.sigRangeChanged.connect(self.updateRegion)
        # self.p2.addItem(self.region, ignoreBounds=True)
        # self.p1.setAutoVisible(y=True)
        # self.trace = trace
        # self.p1data=self.p1.plot(trace, pen="r")
        # self.p2data=self.p2.plot(trace, pen=default_trace_color)
        # self.vLine = pg.InfiniteLine(angle=90, movable=False)
        # self.hLine = pg.InfiniteLine(angle=0, movable=False)
        # self.p1.addItem(self.vLine, ignoreBounds=True)
        # self.p1.addItem(self.hLine, ignoreBounds=True)
        # self.vb = self.p1.vb
        # self.proxy = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        # self.region.setRegion([0, 200])
        # self.p2.vb.mouseDragEvent=self.mouseDragEvent2
        # if self.tiffFig.parent().conditions is not None:
        #     self.update_gray_bars()

#     ##########################################################
#     # Modified by Hyungtae Kim <hyungtk@uci.edu>, in Dec 2014
#     # Gray bars should support sfreq meta as well as `ResponseFig`
#     # I changed name from `addgraybars` - > `update_gray_bars` to let this have right name.
#     #
#     def clear_gray_bars(self):
#         gbars_p1 = [item for item in self.p1.items if hasattr(item, '__graybar__')]
#         gbars_p2 = [item for item in self.p2.items if hasattr(item, '__graybar__')]
#         for gbp1, gbp2 in zip(gbars_p1, gbars_p2):
#             self.p1.removeItem(gbp1)
#             self.p2.removeItem(gbp2)
#
#     def update_gray_bars(self):
#         self.clear_gray_bars()
#         parent = self.tiffFig.parent()
#         cond = parent.conditions
#         meta = parent.sfreq_meta
#         if meta:
#             print 'gray bars will be updated along the current sfreq meta by cursor at #%s' % meta.sfreq_cursor
#         r=Response(self.trace, cond, meta)
#         for o in r.orientations:
#             for rep in o.reps:
#                 a1=pg.LinearRegionItem(
#                     values=[rep.firstFrame,rep.lastFrame],
#                     brush=pg.mkBrush(0, 0, 0, 40), movable=False) #add gray bars
#                 a1.__graybar__ = True
#                 self.p1.addItem(a1)
#                 for l in a1.lines:
#                     self.scene().removeItem(l)
#                 a2=pg.LinearRegionItem(
#                     values=[rep.firstFrame,rep.lastFrame],
#                     brush=pg.mkBrush(0, 0, 0, 40), movable=False) #add gray bars
#                 a2.__graybar__ = True
#                 self.p2.addItem(a2)
#                 for l in a2.lines:
#                     self.scene().removeItem(l)
#     def mouseDragEvent2(self,ev):
#         ev.ignore() # prevent anything from happening
#     def mouseDragEvent1(self,ev):
#         ev.ignore() # prevent anything from happening
#     def update(self):
#         self.region.setZValue(10)
#         minX, maxX = self.region.getRegion()
#         self.p1.setXRange(minX, maxX, padding=0)
#     def updateRegion(self,window, viewRange):
#         rgn = viewRange[0]
#         self.region.setRegion(rgn)
#
#     def mouseMoved(self,evt):
#         pos = evt[0]  ## using signal proxy turns original arguments into a tuple
#         if self.p1.sceneBoundingRect().contains(pos):
#             mousePoint = self.vb.mapSceneToView(pos)
#             index = int(mousePoint.x())
#             if index > 0 and index < len(self.trace):
#                 self.label.setText("<span style='font-size: 12pt'>frame={0},   <span style='color: red'>y={1:.1f}</span>".format(index, self.trace[index]))
#                 self.tiffFig.setCurrentIndex(index)
#             self.vLine.setPos(mousePoint.x())
#             self.hLine.setPos(mousePoint.y())
#
#     def update_trace(self,trace):
#         self.p1data.setData(trace)
#         self.p2data.setData(trace)
