import cStringIO
import shutil
import ujson
import numpy as np
from scipy import io
from sqlalchemy import event
from sqlalchemy.orm import object_session

from pacu.util.path import Path
from pacu.util import identity
from pacu.util.prop.memoized import memoized_property
from pacu.profile import manager

from pacu.core.io.scanbox.view.sbx import ScanboxSBXView
from pacu.core.io.scanbox.view.mat import ScanboxMatView
from pacu.core.io.scanbox.channel import ScanboxChannel
from pacu.core.io.scanbox.model import db as schema
from pacu.core.model.experiment import ExperimentV1

from pacu.core.addons.export import Export
from pacu.core.addons.loadmat import loadmat, spio

opt = manager.instance('opt')
glab = manager.get('db').section('glab')()
userenv = identity.path.userenv

class ScanboxIO(object):
    def __init__(self, path, cur_pane=0):
        self.path = userenv.joinpath('scanbox', path).ensure_suffix('.io')
        self.db_path = self.path.joinpath('db.sqlite3').absolute()
        self.root_mat_path = opt.scanbox_root.joinpath(path).with_suffix('.mat')
        self.mat_path = self.path.joinpath('meta').with_suffix('.mat')
        self.sbx_path = opt.scanbox_root.joinpath(path).with_suffix('.sbx')
        self.cur_pane = cur_pane
        self.confirm_mat() # JZ confirm mat file is copied to io directory
    @property
    def mat(self):
        return ScanboxMatView(self.mat_path)
    @property
    def sbx(self):
        return ScanboxSBXView(self.sbx_path)
    def remove_io(self):
        self.path.rmtree()
    def confirm_mat(self):
        if self.path.is_dir() and not self.mat_path.is_file():
            info = loadmat(self.root_mat_path.str)['info']
            info['stempath'] = self.root_mat_path.stempath.str
            spio.savemat(self.mat_path.str, {'info': info})
    def import_raw(self, condition_id=None):
        if self.path.is_dir():
            raise OSError('{} already exists!'.format(self.path))
        else:
            self.path.mkdir_if_none()
        self.confirm_mat()
        print 'Converting raw data...'
        for nchan in range(self.mat.nchannels):
            ScanboxChannel(self.path.joinpath('{}.chan'.format(nchan))
            ).import_with_io(self)
        print 'Initialize local database...'
        self.initialize_db(condition_id)
        print 'Done!'
        return self.toDict()
    @memoized_property
    def sessionmaker(self):
        maker = schema.get_sessionmaker(self.db_path, echo=False)
        event.listen(maker, 'before_flush', schema.before_flush)
        event.listen(maker, 'after_commit', schema.after_commit)
        return maker
    @memoized_property
    def db_session(self):
        return self.sessionmaker()
    def initialize_db(self, condition_id=None):
        # requires original location...
        schema.recreate(self.db_path, echo=False)
        session = self.db_session
        with session.begin():
            condition = schema.Condition(info=self.mat.toDict())
            session.add(condition)
        if condition_id:
            self.import_condition(condition_id)
    def import_condition(self, id):
        session = self.db_session
        exp = glab.query(ExperimentV1).get(id)
        try:
            with session.begin():
                condition = session.query(schema.Condition).one()
                condition.from_expv1(exp)
                condition.trials.extend([
                    schema.Trial.init_and_update(**trial)
                    for trial in exp])
                condition.imported = True
                condition.exp_id = int(id)
                session.add(condition)
        except Exception as e:
            print 'Condition import failed with reason below,', str(e)

    @memoized_property
    def condition(self):
        # Session = schema.get_sessionmaker(self.db_path, echo=False)
        condition = self.db_session.query(schema.Condition).one()
        condition.expdb = glab.query(ExperimentV1).get(condition.exp_id or '')
        return condition
    @memoized_property
    def ch0(self):
        n_focal_pane = self.condition.info.get('focal_pane_args', {}).get('n', 1)
        print 'Setup a focal pane #{} out of {}...'.format(self.cur_pane, n_focal_pane)
        return ScanboxChannel(self.path.joinpath('0.chan'), n_focal_pane, self.cur_pane)
    @ch0.invalidator
    def setup_focal_pane(self, offset):
        self.cur_pane = offset
        return self
    @memoized_property
    def ch1(self): # not used
        return ScanboxChannel(self.path.joinpath('1.chan'))
    def toDict(self):
        try:
            return dict(info=self.condition.info,
                    has_condition = self.condition.imported,
                workspaces=[ws.name for ws in self.condition.workspaces])
        except Exception as e:
            if 'no such column' in str(e):
                self.fix_db_schema()
                print 'Fixing DB Schema'
                return dict(info=self.condition.info, dbfixed=True,
                        has_condition = self.condition.imported,
                    workspaces=[ws.name for ws in self.condition.workspaces])
            err = dict(type=str(type(e)), detail=str(e))
            return dict(err=err, info=self.mat.toDict())
    def fix_db_schema(self):
        path = self.db_path
        print 'fix', path
        shutil.copy2(path.str, path.with_suffix('.backup.sqlite3').str)
        meta = schema.SQLite3Base.metadata
        bind = self.db_session.bind
        schema.fix_incremental(meta, bind)
    def echo_on(self):
        self.db_session.bind.engine.echo=True
        return self
    def echo_off(self):
        self.db_session.bind.engine.echo=False
        return self
    @classmethod
    def iter_every_io(cls):
        return (cls(path) for path in userenv.joinpath('scanbox').rglob('*.io'))
    @classmethod
    def fix_db_schema_all(cls):
        meta = schema.SQLite3Base.metadata
        for io in ScanboxIO.iter_every_io():
            io.fix_db_schema()
            # bind = io.condition.object_session.bind
            # schema.fix_incremental(meta, bind)
    def export_sfreqfit_data_as_mat(self, wid, rid, contrast):
        roi = self.db_session.query(schema.ROI
            ).filter_by(id=rid, workspace_id=wid).one()
        return roi.export_sfreqfit_data_as_mat(contrast)
    def export_traces_as_mat(self, wid):
        ws = self.db_session.query(schema.Workspace).get(wid)
        sio = cStringIO.StringIO()
        data = {'cell' + str(roi.id): roi.dtoverallmean.value
            for roi in ws.rois if roi.draw_dtoverallmean}
        io.savemat(sio, data)
        return sio.getvalue()
    @staticmethod
    def condition_by_file(filename='db.sqlite3'):
        Session = schema.get_sessionmaker(filename)
        s = Session()
        condition = s.query(schema.Condition).one()
        return s, condition
    def export_trace_of_all_rois_of_all_workspaces(self):
        for ws in self.condition.workspaces:
            wspath = self.path.joinpath('EXPORT-TRACE-' + self.condition.workspaces.first.name)
            wspath.mkdir_if_none()
            for roi in ws.rois:
                path = wspath.joinpath('ROI_{}_trace'.format(roi.id))
                np.save(path.str, roi.dtoverallmean.value)
                path.with_suffix('.npy').rename(path.str)
    def compute_all_rois_of_all_workspaces(self):
        for ws in self.condition.workspaces:
            for roi in ws.rois:
                try:
                    roi.refresh_all()
                except Exception as e:
                    print 'ERROR', e
    def export_excel(self, ids, wsName):
        active_workspace = self.condition.workspaces.filter_by(name=str(wsName))[0]
        #return Export(self.path, wsName, self.condition, str(ids), active_workspace.rois).excel()
        return Export(ScanboxIO(self.path), wsName, self.condition, str(ids)).excel()
    def export_matlab(self, ids, wsName):
        active_workspace = self.condition.workspaces.filter_by(name=str(wsName))[0]
        #return Export(self.path, wsName, self.condition, str(ids), active_workspace.rois).matlab()
        return Export(ScanboxIO(self.path), wsName, self.condition, str(ids)).matlab()
    def export_both(self, ids, wsName):
        active_workspace = self.condition.workspaces.filter_by(name=str(wsName))[0]
        #return Export(self.path, wsName, self.condition, str(ids), active_workspace.rois).both()
        return Export(ScanboxIO(self.path), wsName, self.condition, str(ids)).both()

def open_sqlite(path):
    return schema.get_sessionmaker(path, echo=False)

def upgrade_sqlite(path):
    """
    for io in ScanboxIO.iter_every_io():
    print io.db_path
    upgrade_sqlite(io.db_path)
    """
    import shutil
    path = Path(path)
    Session = open_sqlite(path.str)
    meta = schema.SQLite3Base.metadata
    bind = Session.kw.get('bind')
    shutil.copy2(path.str, path.with_suffix('.backup.sqlite3').str)
    schema.fix_incremental(meta, bind)
    return Session

def fix_contrasts_schema(Session):
    from sqlalchemy.orm import load_only
    session = Session()
    condition = session.query(schema.Condition).options(load_only('id')).one()
    contrast = condition.contrast
    if not condition.exp_id:
        print 'no cond, return'
        return
    exp = glab.query(ExperimentV1).get(condition.exp_id)
    ct = exp.stimulus_kwargs.get('contrast')
    cts = exp.stimulus_kwargs.get('contrasts')
    print ct, cts

    if ct:
        condition.contrast = ct
        condition.contrasts = [ct]
    if cts:
        condition.contrasts = cts
    for ws in session.query(schema.Workspace):
        ws.cur_contrast = contrast
        for roi in ws.rois:
            for dt in roi.dttrialdff0s:
                dt.trial_contrast = contrast
            for dt in roi.dtorientationsmeans:
                dt.trial_contrast = contrast
            for dt in roi.dtorientationbestprefs:
                dt.trial_contrast = contrast
            for dt in roi.dtorientationsfits:
                dt.trial_contrast = contrast
            for dt in roi.dtanovaeachs:
                dt.trial_contrast = contrast
            for dt in roi.dtsfreqfits:
                dt.trial_contrast = contrast
            for dt in roi.dtanovaalls:
                dt.trial_contrast = contrast
    for t in session.query(schema.Trial):
        t.contrast = condition.contrast
    condition.object_session.begin()

import re
import numpy as np
from matplotlib import pyplot
# import ujson
# qwe = glab.query(ExperimentV1).get(1087)
# get_ipython().magic('pylab')
# def plot_timing_diff(id=1087):
#     qwe = glab.query(ExperimentV1).get(id)
#     asd = map(float,
#         [re.match(r'(?P<num>[\d\.]+)\s.*', line).groupdict().get('num')
#             for line in qwe.message.splitlines() if 'Entering' in line])
#     ps = [e-asd[0] for e in asd]
#     lj = [t.get('on_time') for t in qwe.ordered_trials]
#     delayinfo = ('{} sec took to show the '
#         'first trial after synchronization').format(lj[0])
#     try:
#         thediff = np.array(ps) - np.array(lj)
#     except Exception as e:
#         raise e
#     else:
#         pyplot.figure()
#         pyplot.plot(thediff)
#         pyplot.suptitle(qwe.keyword)
#         pyplot.title(delayinfo)
#         pyplot.ylabel('psychopy - labjack in second')
#         pyplot.xlabel('trials in order')

# for io in ScanboxIO.iter_every_io():
#     for ws in io.condition.workspaces:
#         for roi in ws.rois:
#             print len(roi.dtorientationsmeans)
#   # io.condition.object_session.begin()



# q = ScanboxIO('test_ka50_lit_day1/day1_000_003.io')
q = ScanboxIO('/Volumes/Users/ht/dev/current/pacu/tmp/day3_000_011.io')

# q = ScanboxIO('Dario/noMDExc2/P22/P22_000_000.io')
# r = q.condition.workspaces.first.rois.first
# q = ScanboxIO('Dario/P22_000_004.io')

# r = q.condition.workspaces.last.rois.first
# fit = r.dtsfreqfit.refresh()
# cnt = r.contours
# frames = q.condition.io.ch0.mmap # going 8bit does not help
# shape = frames.shape[1:]
# mask = np.zeros(shape, dtype='uint8')
# cv2.drawContours(mask, [cnt], 0, 255, -1)
# x, y, w, h = cv2.boundingRect(np.array([cnt]))
# 
# b_frames = frames[::, y:y+h, x:x+w] # down sampling also could work for large
# print 'FRAME LENGTH', len(b_frames)
# b_mask = mask[y:y+h, x:x+w]
# 
# def trace2(frames, mask):
#     s = time.time()
#     rv = np.array([cv2.mean(frame, mask)[0] for frame in frames], dtype='float64')
#     print 'ELAPSED:', time.time() - s
#     return rv


def ScanboxIOStream(files): # magic protocol... for damn `files` kwargs
    return ScanboxIO(files)

def redump(filename):
    """
    redump('2016-10-11_12_05_11.x.160921.1_P19_004_001.pickle')
    """
    import cPickle
    with open(filename, 'rb') as f:
        data = cPickle.load(f)
    print data.keys()
    result = data['result']
    keyword = data['keyword']
    payload = data['payload']
    errormsg = result.pop('errormsg', None)
    errortype = result.pop('errortype', None)
    model = ExperimentV1(**result)
    for key, val in payload.items():
        for attr in 'clsname pkgname kwargs'.split():
            ett_attr = key + '_' + attr
            ett_val = val.get(attr)
            setattr(model, ett_attr, ett_val)
    off_duration = model.stimulus_kwargs.get('off_duration')
    model.duration = max(t for ts in model.off_time for t in ts) + off_duration
    model.keyword = keyword
    session = glab
    session.add(model)
    session.commit()
    return model


