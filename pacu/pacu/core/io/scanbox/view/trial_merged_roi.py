import runpy
from datetime import datetime

from scipy import io

from pacu.util.prop.memoized import memoized_property
from pacu.core.io.scanbox.model.relationship import flist
from pacu.core.io.scanbox.model.datatag import DTOrientationsMean
from pacu.core.io.scanbox.model.datatag import DTOrientationBestPref
from pacu.core.io.scanbox.model.datatag import DTOrientationsFit
from pacu.core.io.scanbox.model.datatag import DTAnovaEach
from pacu.core.io.scanbox.model.datatag import DTSFreqFit
from pacu.core.io.scanbox.model.datatag import DTAnovaAll

def serialize(o):
    if isinstance(o, dict):
        return {str(key): serialize(val) for key, val in o.items() if val is not None}
    elif isinstance(o, (list, tuple)):
        return [serialize(item) for item in o]
    elif hasattr(o, 'toDict'):
        return serialize(o.toDict())
    elif hasattr(o, '__dict__'):
        return serialize(vars(o))
    elif isinstance(o, unicode):
        return str(o)
    elif isinstance(o, datetime):
        return str(o)
    else:
        return o

class TrialMergedROIView(object):
    """
    roi_id_to_pickup = 1
    workspace1 = io1.condition.workspaces[0] # first workspace
    workspace2 = io2.condition.workspaces[3] # fourth workspace
    workspace3 = io3.condition.workspaces[1] # second workspace
    r = TrialMergedROIView(roi_id_to_pickup, workspace1, workspace2, workspace3)
    r.trials # will give you 1500 sorted trials if each condition 500 trials
    r.refresh() # recompute every datatag
    """
    exc_no_roi = 'One of workspaces does not have an ROI with id {.roi_id}'
    def __init__(self, roi_id, version=2, *workspaces):
        self.roi_id = roi_id
        self.workspaces = workspaces
        self.workspace = self.workspaces[0]
        self.condition = self.workspace.condition
        self.version = version
        self.rois = self.collect_rois()
    def collect_rois(self):
        try:
            if self.version == 1:
                return [
                    ws.rois.filter_by(params={'cell_id': str(self.roi_id)})[0]
                for ws in self.workspaces]
            elif self.version == 2:
                return [
                    ws.rois.filter_by(id=self.roi_id)[0]
                for ws in self.workspaces]
        except: raise Exception(self.exc_no_roi.format(self))
    @memoized_property
    def dff0s(self):
        return flist([datatag for roi in self.rois for datatag in roi.dttrialdff0s])
    @memoized_property
    def dtorientationsmeans(self):
        return flist([
            DTOrientationsMean(trial_sf=sf, trial_contrast=ct)
            for sf in self.condition.sfrequencies
            for ct in self.condition.contrasts])
    @memoized_property
    def dtorientationbestprefs(self):
        return flist([
            DTOrientationBestPref(trial_contrast=ct)
            for ct in self.condition.contrasts])
    @memoized_property
    def dtorientationsfits(self):
        return flist([
            DTOrientationsFit(trial_sf=sf, trial_contrast=ct)
            for sf in self.condition.sfrequencies
            for ct in self.condition.contrasts])
    @memoized_property
    def dtanovaeachs(self):
        return flist([
            DTAnovaEach(trial_sf=sf, trial_contrast=ct)
            for sf in self.condition.sfrequencies
            for ct in self.condition.contrasts])
    @memoized_property
    def dtsfreqfits(self):
        return flist([
            DTSFreqFit(trial_contrast=ct)
            for ct in self.condition.contrasts])
    @memoized_property
    def dtanovaalls(self):
        return flist([
            DTAnovaAll(trial_contrast=ct)
            for ct in self.condition.contrasts])
    def run_module(self, name, datatags, **kwargs):
        for datatag in datatags:
            runpy.run_module(name, run_name='__sbx_stitch__', init_globals=dict(
                workspace=self.workspace, condition=self.condition, roi=None,
                datatag=datatag, dff0s=self.dff0s, **kwargs))
    def refresh_dtorientationsmeans(self):
        module = 'pacu.core.io.scanbox.method.orientations.mean'
        self.run_module(module, self.dtorientationsmeans)
    def refresh_dtorientationbestprefs(self):
        module = 'pacu.core.io.scanbox.method.orientation.bestpref'
        self.run_module(module, self.dtorientationbestprefs)
    def refresh_dtorientationsfits(self):
        module = 'pacu.core.io.scanbox.method.orientations.fit'
        self.run_module(module, self.dtorientationsfits, bestprefs=self.dtorientationbestprefs)
    def refresh_dtanovaeachs(self):
        module = 'pacu.core.io.scanbox.method.anova.each'
        self.run_module(module, self.dtanovaeachs)
    def refresh_dtsfreqfits(self):
        module = 'pacu.core.io.scanbox.method.sfreq.fit'
        self.run_module(module, self.dtsfreqfits, fits=self.dtorientationsfits)
    def refresh_dtanovaalls(self):
        module = 'pacu.core.io.scanbox.method.anova.all'
        self.run_module(module, self.dtanovaalls)
    def refresh(self):
        self.refresh_dtorientationsmeans()
        self.refresh_dtorientationbestprefs()
        self.refresh_dtorientationsfits()
        self.refresh_dtanovaeachs()
        self.refresh_dtsfreqfits()
        self.refresh_dtanovaalls()
        return self
    def serialize(self):
        return serialize(self)
    def savemat(self, filename):
        payload = self.serialize()
        io.savemat(filename, payload)
        return payload
    def toDict(self):
        return dict(
            dtorientationsmeans=self.dtorientationsmeans,
            dtorientationbestprefs=self.dtorientationbestprefs,
            dtorientationsfits=self.dtorientationsfits,
            dtanovaeachs=self.dtanovaeachs,
            dtsfreqfits=self.dtsfreqfits,
            dtanovaalls=self.dtanovaalls,
            condition=self.condition,
            rois=self.rois)

class TrialMergedROIViewByCentroid(TrialMergedROIView):
    def __init__(self, centroid, *workspaces):
        self.centroid = centroid
        self.workspaces = workspaces
        self.workspace = self.workspaces[0]
        self.condition = self.workspace.condition
        self.rois = self.collect_rois()
    def collect_rois(self):
        try: return [
            ws.rois.filter_by(centroid=self.centroid)[0]
            for ws in self.workspaces]
        except: raise Exception(self.exc_no_roi.format(self))
