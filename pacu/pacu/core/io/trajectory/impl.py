from __future__ import division

import shutil
import tifffile
import numpy as np

from datetime import datetime

from pacu.profile import manager
from pacu.util.path import Path
from pacu.util.prop.memoized import memoized_property
from pacu.core.io.trajectory.channel import TrajectoryChannel
from pacu.core.io.trajectory.session import TrajectorySession
from pacu.core.io.trajectory.log.impl import TrajectoryLog
from pacu.core.io.trajectory.response import TrajectoryResponse
from pacu.core.io.trajectory.filter import TrajectoryFilter
from pacu.core.io.scanimage.roi.impl import ROI

# from pacu.core.io.scanimage.response.impl import Response
# from pacu.core.io.scanimage.response.roi import ROIResponse

class TrajectoryIO(object):
    session_name = 'main'
    def __init__(self, path):
        self.path = Path(path).merge_or_join_suffix('.imported', on='.tif')
    @property
    def exists(self):
        return self.path.is_dir()
    @property
    def as_record(self):
        return dict(
            name = self.tiffpath.name,
            user = 'Soyun & Kirstie',
            time = self.datetime.strftime('%H:%M:%S'),
            host = 'IOS',
            desc = self.desc,
            mouse = 'Mouse 3',
            package = self)
    @property
    def desc(self):
        return '{}'.format(
            tifffile.format_size(self.tiffpath.stat().st_size)
        )
    @property
    def datetime(self):
        return datetime.fromtimestamp(
            float(self.tiffpath.stem))
    @property
    def tiffpath(self):
        return self.path.with_suffix('.tif')
    def toDict(self):
        return dict(exists=self.exists, path=self.path.str, sessions=self.sessions)
    @memoized_property
    def tiff(self):
        tiffpath = self.path.with_suffix('.tif')
        file_size = tiffpath.lstat().st_size
        print 'Import from {}...'.format(tiffpath)
        print 'File size {:,} bytes.'.format(file_size)
        return tifffile.imread(tiffpath.str)
    def import_raw(self):
        if self.exists:
            return False
        self.create_package_path()
        print 'Looking for matching VR log file...'
        log = TrajectoryLog.query(self.datetime)
        # it can fail but never reports.
        print 'Converting channel and timestamps...'
        tss = np.fromfile(self.path.with_suffix('.csv').str,
            sep='\n', dtype='float64')
        TrajectoryChannel(self.path.joinpath('channel')
            ).import_raw(self.tiff, tss, log)
        print 'Import done!'
        return self.toDict()
    def create_package_path(self):
        self.path.mkdir()
        print 'Path `{}` created.'.format(self.path.str)
    def remove_package(self):
        shutil.rmtree(self.path.str)
        return self.toDict()
    @memoized_property
    def channel(self):
        tfilter = self.session.opt.get('filter')
        if tfilter:
            if tfilter._indices is not None:
                return TrajectoryChannel(self.path.joinpath('channel')
                    ).set_indices(tfilter._indices)
        return TrajectoryChannel(self.path.joinpath('channel'))
    @property
    def sessions(self):
        return map(TrajectorySession, sorted(self.path.ls('*.session')))
    @memoized_property
    def session(self):
        return TrajectorySession(
            self.path.joinpath(self.session_name).with_suffix('.session'))
    @session.invalidator
    def set_session(self, session_name):
        self.session_name = session_name
        return self
    @memoized_property
    def alog(self): # aligned log in JSON format
        return [
            dict(e=e, x=x, y=y, v=v)
            for e, x, y, v in self.channel.alog[['E', 'X', 'Y', 'V']]]
    @property
    def main_response(self):
        return TrajectoryResponse(self.channel.stat.MEAN)
    def upsert_roi(self, roi_kwargs):
        return self.session.roi.upsert(ROI(**roi_kwargs))
    def upsert_filter(self, filter_kwargs):
        tfilter = TrajectoryFilter(**filter_kwargs)
        tfilter._indices = tfilter.make_indices(self.channel.original_velocity)
        rv = self.session.opt.upsert(tfilter)
        for roi in self.session.roi.values():
            roi.invalidated = True
        self.session.roi.save()
        return rv
    def make_response(self, id):
        roi = self.session.roi[id]
        extras = self.session.roi.values()
        extras.remove(roi)
        main_trace, main_mask = roi.trace(self.channel.mmap)
        neur_trace, neur_mask = roi.neuropil_trace(self.channel.mmap, extras)
        trace = main_trace - neur_trace*0.7
        roi.invalidated = False
        roi.response = TrajectoryResponse(trace)
        return self.session.roi.upsert(roi)
    @memoized_property
    def velocity_stat(self):
        return dict(
            max = self.channel.alog.V.max(),
            mean = self.channel.alog.V.mean(),
            min = self.channel.alog.V.min(),
        )


# path = 'tmp/Soyun/2016-03-04T10-00-37/1457114437.12.tif'
# path = 'tmp/Soyun/2016-03-04T10-00-37/1457114745.57.tif'
# qwe = TrajectoryIO(path)
# a = qwe.session.roi
# velocity filter
# active_pass
# passive_pass
# positive_pass
# band_pass
# none

# qwe.session.roi.clear()
# qwe.session.opt.clear()

# def testdump():
#     path = 'tmp/Dario/2015.12.02/x.151101.2/bV1_Contra_004'
#     qwe = ScanimageIO(path)
#     qwe.session.roi.clear()
#     qwe.session.opt.clear()
#     from pacu.util.identity import path
#     rois = path.cwd.ls('*pickle')[0].load_pickle().get('rois')
#     pgs = [[dict(x=x, y=y) for x, y in roi] for roi in rois]
#     kws = [dict(polygon=p) for p in pgs]
#     for kw in kws:
#         qwe.session.roi.upsert(ROI(**kw))

def TrajectoryIOFetcher(recording, trial, session):
    root = manager.instance('opt').trajectory_root
    path = Path(root).joinpath(recording, trial)
    return TrajectoryIO(path).set_session(session)
