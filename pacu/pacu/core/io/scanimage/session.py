from datetime import datetime
import shutil

from pandas import json

from pacu.util.path import Path
from pacu.util.inspect import repr
from pacu.util.prop.memoized import memoized_property
from pacu.profile import manager
from pacu.core.model.ed.visstim2p import VisStim2P
from pacu.core.model.glams import Mice
from pacu.core.model.analysis import AnalysisV1
from pacu.core.io.scanimage.nmspc import HybridNamespace

# print 'dev overide: pacu.core.io.scanimage.session'
class ScanimageSession(object):
    roi = None
    opt = None
    __repr__ = repr.auto_strict
    def __init__(self, path):
        self.path = Path(path).with_suffix('.session')
        self.package, self.mouse, self.date, self.user = self.path.parts[::-1][1:5]
        self.roi = HybridNamespace.from_path(self.path.joinpath('roi'))
        self.opt = HybridNamespace.from_path(self.path.joinpath('opt'))
    def toDict(self):
        return dict(name=self.path.stem, path=self.path.str)
    @property
    def glams_session(self):
        return manager.get('db').section('glams')()
    @property
    def ed_session(self):
        return manager.get('db').section('ed')()
    def query_experiment_db(self):
        mouse = self.glams_session.query(Mice).filter_by(name=self.mouse).one()
        return self.ed_session.query(VisStim2P).filter_by(
            mouse_id=mouse.id,
            date=self.datetime.date(),
            filename=self.package.rstrip('.imported'))
    @property
    def datetime(self):
        return datetime.strptime(self.date, '%Y.%m.%d')
    @memoized_property
    def ed(self):
        # return Path('tmp/Dario/2016.01.27/r.151117.3/DM9_RbV1_Contra004004.pickle').load_pickle()
        # return Path('ed.2015.12.02.bV1_Contra_004.pickle').load_pickle()
        try:
            return self.query_experiment_db().one()
        except:
            print 'NONE DB ENTITY'
            return None
    @property
    def has_ed(self):
        return bool(self.query_experiment_db().count())
    @property
    def exists(self):
        return self.path.is_dir()
    def create(self):
        print 'create session, mkdir', self.path
        self.path.mkdir()
    def remove(self):
        print 'remove session, rmtree', self.path
        shutil.rmtree(self.path.str)
    def get_rois_json_safe(self):
        rois = []
        total = len(self.roi)
        for index, rv in enumerate(self.roi.values()):
            print  'Check {}/{} ROI...'.format(index + 1, total)
            try:
                json.loads(json.dumps(rv)) # verify
            except Exception as e:
                print 'ROI #{} has problem, "{}", SKIP LOADING!'.format(rv.id, e)
                rv.error = str(e)
                rv.blank = None
                rv.flicker = None
                rv.responses = {}
                rois.append(rv)
            else:
                rois.append(rv)
        return rois
#     def load_rois(self):
#         rois = self.roi.values()
#         total = len(rois)
#         dumps = []
#         for index, roi in enumerate(rois):
#             print  'Loading {}/{} ROI...'.format(index, total)
#             dumps.append(roi)
#         return ujson.dumps(dumps)
# testpath = 'tmp/Dario/2015.12.02/x.151101.2/bV1_Contra_004.imported/main.session'
# qwe = ScanimageSession(testpath)
