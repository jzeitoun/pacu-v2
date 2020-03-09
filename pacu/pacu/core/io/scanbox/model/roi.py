import base64
import operator
import cStringIO
from collections import OrderedDict
from datetime import datetime

import cv2
import numpy as np
from scipy import io
from sqlalchemy import Column, Integer, Boolean, Float, UnicodeText
from sqlalchemy.types import PickleType
from sqlalchemy.orm import object_session

from pacu.core.io.scanbox.model.base import SQLite3Base
from sqlalchemy import inspect
from pacu.core.io.scanbox.model.variant.roi import VTROIParams

origet = operator.attrgetter('ori')
TRIAL_ATTRS = 'on_time off_time ori sf tf contrast sequence order ran flicker blank'.split()

def serialize(o):
    if isinstance(o, dict):
        return {str(key): serialize(val) for key, val in o.items() if val is not None}
    elif isinstance(o, (list, tuple)):
        return [serialize(item) for item in o]
    elif hasattr(o, 'toAltDict'):
        return serialize(o.toAltDict())
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

class ROI(SQLite3Base):
    __tablename__ = 'rois'
    polygon = Column(PickleType, default=[])
    centroid = Column(PickleType, default=dict(x=-1, y=-1))
    neuropil_ratio = Column(Float, default=4.0, nullable=False)
    neuropil_factor = Column(Float, default=0.7, nullable=False)
    neuropil_polygon = Column(PickleType, default=[])
    neuropil_enabled = Column(Boolean, default=True)
    active = Column(Boolean, default=False) # do not use for a while
    draw_dtoverallmean = Column(Boolean, default=False)
    object_session = property(object_session)
    sog_initial_guess = Column(PickleType)
    params = Column(VTROIParams.as_mutable())
    @property
    def contours(self):
        return np.array([[p['x'], p['y']] for p in self.polygon])
    @property
    def neuropil_contours(self):
        return np.array([[p['x'], p['y']] for p in self.neuropil_polygon])
    def dt_ori_by_sf(self, contrast):
        sfs = self.workspace.condition.sfrequencies
        oris = self.workspace.condition.orientations
        trials = self.dttrialdff0s.filter_by(
            trial_contrast=contrast, trial_flicker=False, trial_blank=False)
        return OrderedDict([
            (
                sf,
                OrderedDict([
                (
                    ori,
                    trials.filter_by(trial_sf=sf, trial_ori=ori)
                )
                for ori in oris])
            ) for sf in sfs])

    def before_flush_dirty(self, session, context): # before attached to session
        pass
        # if inspect(self).attrs.polygon.history.has_changes():
        #     for tag in self.datatags:
        #         if not inspect(tag).attrs.value.history.has_changes():
        #             tag.invalidate()
    def before_flush_new(self, session, context):
        self.initialize_datatags()
    def initialize_datatags(self): # order is very important.
        from pacu.core.io.scanbox.model.datatag import DTOverallMean
        from pacu.core.io.scanbox.model.datatag import DTTrialDff0
        from pacu.core.io.scanbox.model.datatag import DTOrientationsMean
        from pacu.core.io.scanbox.model.datatag import DTOrientationBestPref
        from pacu.core.io.scanbox.model.datatag import DTOrientationsFit
        from pacu.core.io.scanbox.model.datatag import DTSFreqFit
        from pacu.core.io.scanbox.model.datatag import DTAnovaAll
        from pacu.core.io.scanbox.model.datatag import DTAnovaEach
        condition = self.workspace.condition
        if not self.dtoverallmean:
            print 'Initialize Overall Mean'
            DTOverallMean(roi=self)
        if not condition.imported:
            return
        if condition.stimulus == 'SparseNoiseStimulus':
            return
        if not self.dttrialdff0s:
            print 'Initialize Trial DFF0'
            n_trials =  len(condition.trials)
            n_ontimes = len(condition.on_times_psychopy)
            if n_trials == n_ontimes:
                # JZ: zip is unnecessary as the trial object already contains on_time;
                # also adding feature to ignore trials with blank frames; 2-26-20

                #for trial, ont in zip(condition.trials, condition.on_times_psychopy):
                #    dt = DTTrialDff0(roi=self)
                #    for attr in TRIAL_ATTRS:
                #        setattr(dt, u'trial_' + attr, getattr(trial, attr))
                #    dt.trial_on_time = ont
                for trial in condition.trials:
                    dt = DTTrialDff0(roi=self)
                    dt.ignore = trial.ignore
                    for attr in TRIAL_ATTRS:
                        setattr(dt, u'trial_' + attr, getattr(trial, attr))
                    dt.trial_on_time = trial.on_time
            else:
                # JZ: adding feature to ignore trials with blank frames; 2-26-20

                #for trial in condition.trials:
                #    dt = DTTrialDff0(roi=self)
                #    for attr in TRIAL_ATTRS:
                #        setattr(dt, u'trial_' + attr, getattr(trial, attr))
                for trial in condition.trials:
                    dt = DTTrialDff0(roi=self)
                    dt.ignore = trial.ignore
                    for attr in TRIAL_ATTRS:
                        setattr(dt, u'trial_' + attr, getattr(trial, attr))
        if not self.dtorientationsmeans:
            print 'Initialize Orientations Mean'
            for sf in condition.sfrequencies:
                for ct in condition.contrasts:
                    for tf in condition.tfrequencies: # added by JZ
                        DTOrientationsMean(roi=self, trial_sf=sf, trial_contrast=ct, trial_tf=tf)
        if not self.dtorientationbestprefs:
            print 'Initialize Orientation Best Pref'
            for ct in condition.contrasts:
                for tf in condition.tfrequencies: # added by JZ
                    DTOrientationBestPref(roi=self, trial_contrast=ct, trial_tf=tf)
        if not self.dtorientationsfits:
            print 'Initialize Orientations Fit'
            for sf in condition.sfrequencies:
                for ct in condition.contrasts:
                    for tf in condition.tfrequencies: # added by JZ
                        DTOrientationsFit(roi=self, trial_sf=sf, trial_contrast=ct, trial_tf=tf)
        if not self.dtanovaeachs:
            print 'Initialize Anova Each'
            for sf in condition.sfrequencies:
                for ct in condition.contrasts:
                    for tf in condition.tfrequencies: # added by JZ
                        DTAnovaEach(roi=self, trial_sf=sf, trial_contrast=ct, trial_tf=tf)
        if not self.dtsfreqfits:
            print 'Initialize SFreq Fit'
            for ct in condition.contrasts:
                for tf in condition.tfrequencies: # added by JZ
                    DTSFreqFit(roi=self, trial_contrast=ct, trial_tf=tf)
        if not self.dtanovaalls:
            print 'Initialize Anova All'
            for ct in condition.contrasts:
                for tf in condition.tfrequencies: # added by JZ
                    DTAnovaAll(roi=self, trial_contrast=ct, trial_tf=tf)
    def refresh_orientations_fit(self):
       print 'REFRESH OriFit' # used in ember/app/pods/roi/model.js
       for tag in self.dtorientationsfits: tag.refresh()

    def refresh_stats_only(self): # added by JZ, compute custom traces
        print 'REFRESH Orientations'
        for tag in self.dtorientationsmeans: tag.refresh()
        print 'REFRESH BEST PREF'
        for tag in self.dtorientationbestprefs: tag.refresh() # <- global o_pref made here
        self.refresh_orientations_fit() # <- each r_max made here
        print 'REFRESH SFreqFit'
        for tag in self.dtsfreqfits: tag.refresh() # <- requires r_max, each peak_sfreq made here
        print 'REFRESH Anova All'
        for tag in self.dtanovaalls: tag.refresh()
        print 'REFRESH Anova Each'
        for tag in self.dtanovaeachs: tag.refresh()

    def refresh_all(self):
        print 'REFRESH TRACE'
        condition = self.workspace.condition
        self.dtoverallmean.refresh()
        if condition.stimulus == 'SparseNoiseStimulus':
            return
        print 'REFRESH df/f0'
        for tag in self.dttrialdff0s: tag.refresh()
        print 'REFRESH Orientations'
        for tag in self.dtorientationsmeans: tag.refresh()
        print 'REFRESH BEST PREF'
        for tag in self.dtorientationbestprefs: tag.refresh() # <- global o_pref made here
        self.refresh_orientations_fit() # <- each r_max made here
        print 'REFRESH SFreqFit'
        for tag in self.dtsfreqfits: tag.refresh() # <- requires r_max, each peak_sfreq made here
        print 'REFRESH Anova All'
        for tag in self.dtanovaalls: tag.refresh()
        print 'REFRESH Anova Each'
        for tag in self.dtanovaeachs: tag.refresh()
        # print 'Bootstrap SF'
        # for tag in dts6: tag.refresh()
    def export(self):
        fields = ('polygon', 'neuropil_ratio', 'params',
            'neuropil_enabled', 'neuropil_factor', 'neuropil_polygon')
        attrs = {f: getattr(self, f) for f in fields}
        return dict(id=self.id, attrs=attrs)
    def export_sfreqfit_data_as_mat(self, contrast):
        sio = cStringIO.StringIO()
        value = self.dtsfreqfits.filter_by(trial_contrast=contrast).first.value
        io.savemat(sio, value)
        return sio.getvalue()
    def toAltDict(self):
        resobj = dict(
            type=self.__tablename__,
            id=self.id,
            attributes=self.attributes,
            relationships=self.relationships,
            dff0s=self.dttrialdff0s,
            dtorientationsmeans=self.dtorientationsmeans,
            dtorientationbestprefs=self.dtorientationbestprefs,
            dtorientationsfits=self.dtorientationsfits,
            dtanovaeachs=self.dtanovaeachs,
            dtsfreqfits=self.dtsfreqfits,
            dtanovaalls=self.dtanovaalls,
            condition=self.workspace.condition
            )
        if hasattr(self, 'meta'):
            resobj['attributes']['meta'] = self.meta
        return resobj

    def serialize(self):
        return serialize(self)

    def to_dict(self, frame_offset):

        print('exporting roi {} to dict'.format(self.id))

        dff0_by_trial = {
            'cls': 'TaskResult',
            'inputs': {},
            'params': {
                'background_ratio': self.neuropil_factor,
                'frame_offset':     frame_offset
            },
            'output': {
                'traces': [t.value['on'] for t in self.dttrialdff0s if t.value],
            }
        }

        orientations_mean = {
            'cls': 'TaskResult',
            'inputs': {
                'trials': [{
                    'orientations': [t.indices[ori] for ori in t.indices],
                    'spatial_frequency': t.trial_sf,
                    'temporal_frequency': t.trial_tf,
                    'contrast': t.trial_contrast,
                } for t in self.dtorientationsmeans],
            },
            'params': {},
            'output': {
                'traces': [t.matrix for t in self.dtorientationsmeans]
            }
        }

        mean_orientations_fit = {
            'cls': 'TaskResult',
            'inputs': {},
            'params': {
                'a1_max':     self.dtorientationsfits[0].sog_params.a1_max,
                'a1_min':     self.dtorientationsfits[0].sog_params.a1_min,
                'a2_max':     self.dtorientationsfits[0].sog_params.a2_max,
                'a2_min':     self.dtorientationsfits[0].sog_params.a2_min,
                'offset_max': self.dtorientationsfits[0].sog_params.offset_max,
                'offset_min': self.dtorientationsfits[0].sog_params.offset_min,
                'sigma_max':  self.dtorientationsfits[0].sog_params.sigma_max,
                'sigma_min':  self.dtorientationsfits[0].sog_params.sigma_min,
            },
            'output': {
                'orientation': [zip(fit.value['x'],fit.value['y_fit'])for fit in self.dtorientationsfits if fit.value]
            }
        }

        orientation_pref_fit = {
            'cls': 'TaskResult',
            'inputs': {},
            'params': {},
            'output': {
                'orientation': self.dtorientationbestprefs[0].value
            }
        }

        spatial_frequency_anova = {
            'cls': 'TaskResult',
            'inputs': {},
            'params': {},
            'output': {
                'f': [t.f for t in self.dtanovaeachs],
                'p': [t.p for t in self.dtanovaeachs]
            }
        }

        anova_all = {
            'cls': 'TaskResult',
            'inputs': {},
            'params': {},
            'output': {
                'f': self.dtanovaalls[0].value['f'],
                'p': self.dtanovaalls[0].value['p']
            } if self.dtanovaalls[0].value else {'f': None, 'p': None}
        }

        spatial_frequency_dog_fit = {
            'cls': 'TaskResult',
            'inputs': {
                'spatial_frequencies': self.dtsfreqfits[0].value['sfx'],
                'amplitudes':          self.dtsfreqfits[0].value['sfy'],
            } if self.dtsfreqfits[0].value else {'spatial_frequencies': None, 'amplitudes': None},
            'params': {},
            'output': {
                'spatial_frequencies': self.dtsfreqfits[0].value['dog_x_ext'],
                'amplitudes':          self.dtsfreqfits[0].value['dog_y_ext'],
            } if self.dtsfreqfits[0].value else {'spatial_frequencies': None, 'amplitudes': None},
        }

        roi_model = {
            'cls':                  'Roi',
            'coordinates':          [[coord['x'], coord['y']] for coord in self.polygon] if self.polygon else [],
            'surround_offset':      self.neuropil_ratio,
            'analysis':             {
                'dff0_by_trial':             dff0_by_trial,
                'orientations_mean':         orientations_mean,
                'mean_orientations_fit':     mean_orientations_fit,
                'orientation_pref_fit':      orientation_pref_fit,
                'spatial_frequency_anova':   spatial_frequency_anova,
                'anova_all':                 anova_all,
                'spatial_frequency_dog_fit': spatial_frequency_dog_fit
            }
        }

        return roi_model
