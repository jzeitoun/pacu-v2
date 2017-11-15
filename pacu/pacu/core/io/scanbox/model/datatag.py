import runpy
import sys
import traceback
import importlib

from sqlalchemy.sql import func
from sqlalchemy import Column, Unicode, Float, Boolean, Integer, DateTime
from sqlalchemy.types import PickleType

from pacu.core.io.scanbox.model.base import SQLite3Base
from pacu.core.io.scanbox.model.variant.dtorientationsfit import VTSoGParams
from pacu.core.io.scanbox.model.variant.dtorientationsmeans import VTOriMeansParams

basemodule = 'pacu.core.io.scanbox.method'

class Datatag(object):
    updated_at = Column(DateTime, onupdate=func.now())
    # exception
    etype = Column(Unicode(128))
    etext = Column(Unicode)
    # dynamic
    value = NotImplemented
    # search trials
    trial_on_time = Column(Float)
    trial_off_time = Column(Float)
    trial_ori = Column(Float)
    trial_sf = Column(Float)
    trial_tf = Column(Float)
    trial_contrast = Column(Float)
    trial_sequence = Column(Integer)
    trial_order = Column(Integer)
    trial_ran = Column(Integer)
    trial_flicker = Column(Boolean)
    trial_blank = Column(Boolean)

    def invalidate(self):
        self.value = None
    def refresh(self):
        roi = self.roi
        workspace = roi.workspace
        condition = roi.workspace.condition
        module = '.'.join((basemodule, self.category, self.method))
        try:
            runpy.run_module(module, run_name='__sbx_main__', init_globals=dict(
                workspace=workspace,
                condition=condition,
                roi=roi,
                datatag=self,
            ))
        except Exception as e:
            print '\n======== exception on datatag ========'
            traceback.print_exception(*sys.exc_info())
            print '======== exception on datatag ========\n'
            self.etype = unicode(type(e))
            self.etext = unicode(e)
            raise e
        else:
            self.etype = None
            self.etext = None
        return self

class DTOverallMean(Datatag, SQLite3Base):
    __tablename__ = 'dtoverallmeans'
    category = 'overall'
    method = 'mean'
    value = Column(PickleType, default=[])
class DTTrialDff0(Datatag, SQLite3Base): # kind of private
    __tablename__ = 'dttrialdff0s'
    category = 'trial'
    method = 'dff0'
    value = Column(PickleType, default=[])
class DTOrientationsMean(Datatag, SQLite3Base):
    __tablename__ = 'dtorientationsmeans'
    category = 'orientations'
    method = 'mean'
    indices = Column(PickleType, default={})
    matrix = Column(PickleType, default=[])
    meantrace = Column(PickleType, default=[])
    on_frames = Column(Integer)
    bs_frames = Column(Integer)
    params = Column(VTOriMeansParams.as_mutable())
class DTOrientationBestPref(Datatag, SQLite3Base):
    __tablename__ = 'dtorientationbestprefs'
    category = 'orientation'
    method = 'bestpref'
    value = Column(Float)
    peak_sf = Column(Float)
    peak_sf_index = Column(Integer)
class DTOrientationsFit(Datatag, SQLite3Base):
    __tablename__ = 'dtorientationsfits'
    category = 'orientations'
    method = 'fit'
    value = Column(PickleType, default={})
    sog_params = Column(VTSoGParams.as_mutable())
class DTSFreqFit(Datatag, SQLite3Base):
    __tablename__ = 'dtsfreqfits'
    category = 'sfreq'
    method = 'fit'
    value = Column(PickleType, default={})
class DTAnovaAll(Datatag, SQLite3Base):
    __tablename__ = 'dtanovaalls'
    category = 'anova'
    method = 'all'
    value = Column(PickleType, default={})
class DTAnovaEach(Datatag, SQLite3Base):
    __tablename__ = 'dtanovaeachs'
    category = 'anova'
    method = 'each'
    f = Column(PickleType)
    p = Column(PickleType)

"""
add datatag derived class in datatag.py
add python method file
add relationship and __all__
modify roi.py initialize and refresh
fix schema incremental
add ember model (with same fields)
define relationship field in roi.js
modify synchonizeDataTags
modify include attr in route
need to append datatable?
"""
