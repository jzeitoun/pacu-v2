import re
from collections import namedtuple
from datetime import datetime

from sqlalchemy import Column, Integer, UnicodeText, Float, Boolean, DateTime
from sqlalchemy.orm import object_session
from sqlalchemy.types import PickleType

from pacu.core.io.scanbox.model.base import SQLite3Base

Times = namedtuple('Times', 'on off')
re_ts = re.compile(r'(?P<ts>[\d\.]+)\s.*')

class Condition(SQLite3Base):
    __tablename__ = 'conditions'
    info = Column(PickleType)
    exp_id = Column(Integer)
    imported = Column(Boolean, default=False)
    pixel_x = Column(Integer)
    pixel_y = Column(Integer)
    dist = Column(Float)
    width = Column(Float)
    height = Column(Float)
    gamma = Column(Float)
    contrast = Column(Float, default=1.0)
    on_duration = Column(Float)
    off_duration = Column(Float)
    repetition = Column(Integer)
    projection = Column(UnicodeText)
    stimulus = Column(UnicodeText)
    handler = Column(UnicodeText)
    keyword = Column(UnicodeText)
    message = Column(UnicodeText)
    trial_list = Column(PickleType, default=[])
    contrasts = Column(PickleType, default=[])
    orientations = Column(PickleType, default=[])
    sfrequencies = Column(PickleType, default=[])
    tfrequencies = Column(PickleType, default=[])
    exp_created_at = Column(DateTime)
    object_session = property(object_session)
    expdb = None
    @property
    def framerate(self):
        return self.info.get('framerate')
    @property
    def has_better_timing(self):
        return self.exp_created_at and \
            self.exp_created_at > datetime(2017, 1, 1)
    @property
    def on_times_psychopy_log(self):
        message = self.message or ''
        tss_str = [re_ts.match(line).group('ts')
            for line in message.splitlines() if 'Entering trial #' in line]
        tss = map(float, tss_str)
        return [ts-tss[0] for ts in tss]
    @property
    def on_times_psychopy_trial(self):
        return [t.on_time for t in self.trials]
    @property
    def on_times_psychopy(self):
        """
        As of 2017, timing is better than parsing log message.
        Check with `has_better_timing` for the condition of new timings.
        then use values of on_time directly.
        """
        if self.has_better_timing:
            return self.on_times_psychopy_trial
        else:
            return self.on_times_psychopy_log
    def from_expv1(self, entity):
        """
        Read from pacu.core.model.experiment.ExperimentV1
        """
        init = {}
        self.trial_list = entity.trial_list.tolist()
        payload = entity.payload
        self.keyword = entity.keyword
        self.projection = entity.projection_clsname
        self.stimulus = entity.stimulus_clsname
        self.handler = entity.handler_clsname
        self.message = entity.message
        self.exp_created_at = entity.created_at
        for k, v in entity.monitor_kwargs.items():
            setattr(self, k, v)
        for k, v in entity.stimulus_kwargs.items():
            setattr(self, k, v)
        if not self.contrasts:
            self.contrasts = [self.contrast]
    @property
    def io(self):
        from pacu.core.io.scanbox.impl2 import ScanboxIO
        # TODO: still has problem with relative paths
        return ScanboxIO(self.info.get('iopath'))
    def append_workspace(self, name, pane=None):
        from pacu.core.io.scanbox.model import db as schema
        with self.object_session.begin():
            if not self.contrasts:
                self.contrasts = [self.contrast]
            ws = schema.Workspace(name=name, condition=self)
            if pane is not None:
                ws.cur_pane = pane
            if self.sfrequencies:
                ws.cur_sfreq = self.sfrequencies[0]
            if self.contrasts:
                ws.cur_contrast = self.contrasts[0]
            # added for temporal frequency addition (JZ)
            if self.tfrequencies:
                ws.cur_tfreq = self.tfrequencies[0]
    def append_workspace_with_focal_pane(self, name, pane):
        self.append_workspace(name, pane)
    @property
    def timings(self):
        times = self.trials.map_by('on_time', 'off_time')
        return [(on, off, off-on-self.on_duration) for on, off in zip(times['on_time'], times['off_time'])]

    def to_dict(self, owner, exp_name, project_name, animal, viewing, hemisphere, session_id, acquisition_id, workspace=None):

        trial_models = []
        for trial in self.trial_list:
            if trial['flicker']:
                typ = 'flicker'
            elif trial['blank']:
                typ = 'blank'
            else:
                typ = 'texture'

            trial_models.append({
                'cls': 'StimulusGratingTrial',
                'type': typ,
                'texture': 'sin',
                'orientation': trial['ori'],
                'contrast': trial['contrast'],
                'temporal_frequency': trial['tf'],
                'spatial_frequency': trial['sf'],
            })

        stimulus_model = {
            'cls':                      'StimulusGrating',
            'viewing_eyes':             viewing,
            'view_distance':            self.dist,
            'projection':               self.projection.replace('Projection', ''),
            'viewport_height_cm':       self.height,
            'viewport_height_px':       self.pixel_y,
            'viewport_width_cm':        self.width,
            'viewport_width_px':        self.pixel_x,
            'gamma':                    self.gamma,

            'handler':                 self.handler.replace('ExpV1Handler', 'scanbox'),

            'repetitions':              int(self.repetition),
            'textures':                 ['sin'],
            'contrasts':                self.contrasts,
            'orientations':             self.orientations,
            'temporal_frequencies':     self.tfrequencies,
            'spatial_frequencies':      self.sfrequencies,

            'stimulus_on_duration':     self.on_duration,
            'blank_duration':           self.off_duration,
            'flicker_duration':         self.off_duration,
            'n_trials':                 len(self.trial_list),
            'trials':                   trial_models,

            'log':                      self.message
        }

        self.info.update({'system': 'Neurolabware-Gandhi', 'cls': 'ImageMeta'})

        image_model = {
            'owner': owner,
            'cls': 'Image',
            'name': self.info['sbxpath'],
            'sample': animal,
            'session': session_id,
            'acquisition': acquisition_id,
            'hemisphere': hemisphere,
            'acquisition_date': self.exp_created_at,
            'metadata': self.info,
            'stimulus': stimulus_model,
        }

        if workspace:
            ws = self.workspaces.filter_by(name=str(workspace))[0]
            workspace_models = [ws.to_dict(owner, exp_name, project_name)]
        else:
            workspace_models = [ws.to_dict(owner, exp_name, project_name) for ws in self.workspaces]

        # add in ifo we couldn't add earlier
        for ws in workspace_models:
            ws['images'] = [image_model]
            for ov in ws['overlays']:
                ov['images'] = [image_model]

        return workspace_models
