from sqlalchemy import Column, Integer, Unicode, ForeignKey
from sqlalchemy.orm import join
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from pacu.core.io.scanbox.model.workspace import Workspace
from pacu.core.io.scanbox.model.roi import ROI
from pacu.core.io.scanbox.model.ephys_correlation import EphysCorrelation
from pacu.core.io.scanbox.model.colormap import Colormap
from pacu.core.io.scanbox.model.action import Action
from pacu.core.io.scanbox.model.condition import Condition
from pacu.core.io.scanbox.model.trial import Trial

class flist(list):
    @property
    def first(self):
        return self[0]
    @property
    def last(self):
        return self[-1]
    def filter_by(self, **kwargs):
        return flist([e for e in self
            if all(getattr(e, k) == v for k, v in kwargs.items())
        ])
    def map_by(self, *attrs):
        return {attr: [getattr(e, attr) for e in self] for attr in attrs}

EphysCorrelation.workspace_id = Column(Integer, ForeignKey(Workspace.id))
Colormap.workspace_id = Column(Integer, ForeignKey(Workspace.id))
ROI.workspace_id = Column(Integer, ForeignKey(Workspace.id))
Workspace.condition_id = Column(Integer, ForeignKey(Condition.id))
Trial.condition_id = Column(Integer, ForeignKey(Condition.id))

from pacu.core.io.scanbox.model.datatag import DTOverallMean
DTOverallMean.roi_id = Column(Integer, ForeignKey(ROI.id))
ROI.dtoverallmean = relationship(DTOverallMean, order_by=DTOverallMean.id,
    uselist=False,
    cascade='all, delete-orphan',
    backref='roi',
    lazy='select')
from pacu.core.io.scanbox.model.datatag import DTTrialDff0
DTTrialDff0.roi_id = Column(Integer, ForeignKey(ROI.id))
ROI.dttrialdff0s = relationship(DTTrialDff0, order_by=DTTrialDff0.id,
    cascade='all, delete-orphan',
    collection_class=flist,
    backref='roi',
    lazy='select')
from pacu.core.io.scanbox.model.datatag import DTOrientationsMean
DTOrientationsMean.roi_id = Column(Integer, ForeignKey(ROI.id))
ROI.dtorientationsmeans = relationship(DTOrientationsMean, order_by=DTOrientationsMean.id,
    cascade='all, delete-orphan',
    collection_class=flist,
    backref='roi',
    lazy='select')
from pacu.core.io.scanbox.model.datatag import DTOrientationBestPref
DTOrientationBestPref.roi_id = Column(Integer, ForeignKey(ROI.id))
ROI.dtorientationbestprefs = relationship(DTOrientationBestPref, order_by=DTOrientationBestPref.id,
    cascade='all, delete-orphan',
    collection_class=flist,
    backref='roi',
    lazy='select')
from pacu.core.io.scanbox.model.datatag import DTOrientationsFit
DTOrientationsFit.roi_id = Column(Integer, ForeignKey(ROI.id))
ROI.dtorientationsfits = relationship(DTOrientationsFit, order_by=DTOrientationsFit.id,
    cascade='all, delete-orphan',
    collection_class=flist,
    backref='roi',
    lazy='select')
from pacu.core.io.scanbox.model.datatag import DTSFreqFit
DTSFreqFit.roi_id = Column(Integer, ForeignKey(ROI.id))
ROI.dtsfreqfits = relationship(DTSFreqFit, order_by=DTSFreqFit.id,
    cascade='all, delete-orphan',
    collection_class=flist,
    backref='roi',
    lazy='select')
from pacu.core.io.scanbox.model.datatag import DTAnovaAll
DTAnovaAll.roi_id = Column(Integer, ForeignKey(ROI.id))
ROI.dtanovaalls = relationship(DTAnovaAll, order_by=DTAnovaAll.id,
    cascade='all, delete-orphan',
    collection_class=flist,
    backref='roi',
    lazy='select')
from pacu.core.io.scanbox.model.datatag import DTAnovaEach
DTAnovaEach.roi_id = Column(Integer, ForeignKey(ROI.id))
ROI.dtanovaeachs = relationship(DTAnovaEach, order_by=DTAnovaEach.id,
    cascade='all, delete-orphan',
    collection_class=flist,
    backref='roi',
    lazy='select')

# this work but this is not query-enabled style
# Workspace.dtoverallmeans = association_proxy('rois', 'dtoverallmean')
# below is instrumented attribute version
Workspace.dtoverallmeans = relationship(DTOverallMean,
    secondary=join(ROI, DTOverallMean),
    primaryjoin=Workspace.id == ROI.workspace_id,
    secondaryjoin=ROI.draw_dtoverallmean & (ROI.id == DTOverallMean.roi_id),
    collection_class=flist,
    viewonly=True,
    lazy='select'
)

Workspace.colormaps = relationship(Colormap, order_by=Colormap.id,
    collection_class=flist,
    cascade='all, delete-orphan',
    backref='workspace',
    lazy='select')
Workspace.rois = relationship(ROI, order_by=ROI.id,
    collection_class=flist,
    cascade='all, delete-orphan',
    backref='workspace',
    lazy='select')
Workspace.ecorrs = relationship(EphysCorrelation, order_by=EphysCorrelation.id,
    collection_class=flist,
    cascade='all, delete-orphan',
    backref='workspace',
    lazy='select')
Condition.workspaces = relationship(Workspace, order_by=Workspace.id,
    collection_class=flist,
    cascade='all, delete-orphan',
    backref='condition',
    lazy='select')
Condition.trials = relationship(Trial, order_by=Trial.id,
    collection_class=flist,
    cascade='all, delete-orphan',
    backref='condition',
    lazy='select')

__all__ = ('Workspace ROI Colormap '
           'DTOverallMean DTTrialDff0 DTOrientationsMean '
           'DTOrientationBestPref '
           'DTAnovaEach '
           'DTOrientationsFit DTSFreqFit DTAnovaAll '
           'EphysCorrelation Action Condition Trial').split()
