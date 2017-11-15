import numpy as np

from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import QObject

from ext.console import debug
from ext.model.session import s
from ext.model.analysis import Analysis
from windows import ROI

class ExternalROISet(list):
    objects = ()
    view = None
    def show(self, view):
        self.view = view
        self.objects = self.render(external=True)
    def hide(self):
        for roi in self.objects:
            roi.delete()
        self.objects = []
    def render(self, external=True):
        return [
            ROI(np.array([point[0] for point in roi['contour']]),
            self.view, roi['label'], external=external)
            for roi in self
        ]

def pull(id):
    return s.query(Analysis).get(id).data['ROIs']

class EventHandler(QObject):
    def on_render(self, should_do):
        print 'caklin on render'
        cell = self.sender().parent()
        if not cell.ext_roi_set:
            cell.ext_roi_set = ExternalROISet(pull(cell.analysis_id))
        if should_do:
            cell.ext_roi_set.show(self.main.tiffFig)
        else:
            cell.ext_roi_set.hide()

    def on_import(self, *args, **kwargs):
        cell = self.sender().parent()
        nrow, analysis_id = cell.nrow, cell.analysis_id
        msg = ("Import will merge ROIs of analysis #%s into "
                "the current analysis." % (nrow + 2))
        reply = QMessageBox.question(self.view,
            'Message', msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            render_btn = cell.children()[1]
            render_btn.setChecked(False)
            self.on_render(False)
            self.merge_rois(cell)

    def merge_rois(self, cell):
        rois = self.main.persistant['ROIs']
        rois.extend(cell.ext_roi_set)
        cell.ext_roi_set.render(external=False)

class ROITableController(object):
    def __init__(self, view, main):
        self.view = view
        self.main = main
        self.handler = EventHandler()
        self.handler.view = view
        self.handler.main = main
    def on(self, eventname):
        return getattr(self.handler, 'on_%s' % eventname)
