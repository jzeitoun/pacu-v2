# from sqlalchemy import event
# from sqlalchemy.orm import object_session

import numpy as np
import pandas as pd
import cv2

from pacu.util.path import Path
from pacu.util import identity
from pacu.util.prop.memoized import memoized_property
from pacu.profile import manager

# from pacu.core.io.scanbox.view.sbx import ScanboxSBXView
# from pacu.core.io.scanbox.view.mat import ScanboxMatView
# from pacu.core.io.scanbox.channel import ScanboxChannel
# from pacu.core.io.scanbox.model import db as schema
# from pacu.core.model.experiment import ExperimentV1

opt = manager.instance('opt')
xulab = manager.get('db').section('xulab')
userenv = identity.path.userenv

def readcam(path):
    cap = cv2.VideoCapture(path)
    length = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    print 'Read {} frames...'.format(length)
    fs = np.array([cap.read()[1] for n in range(length)])
    cap.release()
    return fs

class MiniscopeIO(object):
    def __init__(self, path):
        print 'MINISCOPE', path
        self.path = userenv.joinpath('miniscope', path).ensure_suffix('.io')
        self.db_path = self.path.joinpath('db.sqlite3').absolute()
        self.raw_path = opt.miniscope_root.joinpath(path).stempath
        # self.mat_path = opt.miniscope_root.joinpath(path).with_suffix('.mat')
        # self.sbx_path = opt.miniscope_root.joinpath(path).with_suffix('.sbx')
#     @property
#     def bhcam(self):
#         return self.raw_path.joinpath('
#     @property
#     def sbx(self):
#         return ScanboxSBXView(self.sbx_path)
#     def remove_io(self):
#         self.path.rmtree()
    def import_raw(self, condition_id=None):
        if self.path.is_dir():
            raise OSError('{} already exists!'.format(self.path))
        else:
            self.path.mkdir_if_none()

        print 'Importing behavior movie...'
        with open(self.path.joinpath('bhcam-mmap.npy').str, 'w') as mm:
            for cam in sorted(self.raw_path.glob('behavCam*')):
                mm.write(readcam(cam.str).tostring())
        print 'Importing miniscope movie...'
        with open(self.path.joinpath('mscam-mmap.npy').str, 'w') as mm:
            for cam in sorted(self.raw_path.glob('msCam*')):
                mm.write(readcam(cam.str).tostring())
        print 'Importing timestamp data..'
        name_map = dict(camNum='CAM_NUM', frameNum='FRAME_NUM', sysClock='SYS_CLOCK', buffer='BUFFER')
        df = pd.read_csv(self.raw_path.joinpath('timestamp.dat').str, sep='\t').rename_axis(name_map, axis='columns')
        gp = df.groupby(['CAM_NUM'])
        (_, cam0), (_, cam1) = gp
        cam0 = cam0.drop('CAM_NUM', axis='columns').set_index('FRAME_NUM')
        cam1 = cam1.drop('CAM_NUM', axis='columns').set_index('FRAME_NUM')
        np.save(self.path.joinpath('cam0-timestamp.npy').str, cam0.to_records())
        np.save(self.path.joinpath('cam1-timestamp.npy').str, cam1.to_records())

# cap = cv2.VideoCapture(str(bcams[0]))
# width = 319
# height = 188
# nframes = 1196
# 
#     width  = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
#     fps    = float(cap.get(cv2.cv.CV_CAP_PROP_FPS))
# qwe = np.memmap('bcam-mmap.npy', mode='r', dtype=np.uint8, shape=(nframes, height, width, 3))























        # for nchan in range(self.mat.nchannels):
        #     ScanboxChannel(self.path.joinpath('{}.chan'.format(nchan))
        #     ).import_with_io(self)
        # print 'Initialize local database...'
        # self.initialize_db(condition_id)
        # print 'Done!'
        # return self.toDict()
#     @memoized_property
#     def sessionmaker(self):
#         maker = schema.get_sessionmaker(self.db_path, echo=False)
#         event.listen(maker, 'before_flush', schema.before_flush)
#         event.listen(maker, 'after_commit', schema.after_commit)
#         return maker
#     @memoized_property
#     def db_session(self):
#         return self.sessionmaker()
#     def initialize_db(self, condition_id=None):
#         # requires original location...
#         schema.recreate(self.db_path, echo=False)
#         session = self.db_session
#         with session.begin():
#             condition = schema.Condition(info=self.mat.toDict())
#             session.add(condition)
#         if condition_id:
#             self.import_condition(condition_id)
#     def import_condition(self, id):
#         session = self.db_session
#         exp = glab().query(ExperimentV1).get(id)
#         try:
#             with session.begin():
#                 condition = session.query(schema.Condition).one()
#                 condition.from_expv1(exp)
#                 condition.trials.extend([
#                     schema.Trial.init_and_update(**trial)
#                     for trial in exp])
#                 condition.imported = True
#                 condition.exp_id = int(id)
#                 session.add(condition)
#         except Exception as e:
#             print 'Condition import failed with reason below,', str(e)
# 
#     @memoized_property
#     def condition(self):
#         # Session = schema.get_sessionmaker(self.db_path, echo=False)
#         return self.db_session.query(schema.Condition).one()
#     @memoized_property
#     def ch0(self):
#         return ScanboxChannel(self.path.joinpath('0.chan'))
#     @memoized_property
#     def ch1(self):
#         return ScanboxChannel(self.path.joinpath('1.chan'))
#     def toDict(self):
#         try:
#             return dict(info=self.condition.info,
#                     has_condition = self.condition.imported,
#                 workspaces=[ws.name for ws in self.condition.workspaces])
#         except Exception as e:
#             if 'no such column' in str(e):
#                 self.fix_db_schema()
#                 print 'Fixing DB Schema'
#                 return dict(info=self.condition.info, dbfixed=True,
#                         has_condition = self.condition.imported,
#                     workspaces=[ws.name for ws in self.condition.workspaces])
#             err = dict(type=str(type(e)), detail=str(e))
#             return dict(err=err, info=self.mat.toDict())
#     def fix_db_schema(self):
#         meta = schema.SQLite3Base.metadata
#         bind = self.db_session.bind
#         schema.fix_incremental(meta, bind)
#     def echo_on(self):
#         self.db_session.bind.engine.echo=True
#         return self
#     def echo_off(self):
#         self.db_session.bind.engine.echo=False
#         return self
#     @classmethod
#     def iter_every_io(cls):
#         return (cls(path) for path in userenv.joinpath('scanbox').rglob('*.io'))
#     @classmethod
#     def fix_db_schema_all(cls):
#         meta = schema.SQLite3Base.metadata
#         for io in ScanboxIO.iter_every_io():
#             bind = io.condition.object_session.bind
#             schema.fix_incremental(meta, bind)
#     def export_sfreqfit_data_as_mat(self, wid, rid):
#         roi = self.db_session.query(schema.ROI
#             ).filter_by(id=rid, workspace_id=wid).one()
#         return roi.export_sfreqfit_data_as_mat()
# qwe = MiniscopeIO('ht/trial1.io')
