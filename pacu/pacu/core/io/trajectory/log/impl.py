import time
import calendar
from datetime import datetime
from datetime import timedelta

from scipy import signal
import numpy as np

from pacu.profile import manager
from pacu.util.prop.memoized import memoized_property
from pacu.util.path import Path
from pacu.core.io.trajectory.log.position import Position
from pacu.core.io.trajectory.log import velocity

# offset = time.timezone if (time.localtime().tm_isdst != 1) else time.altzone
# offset = offset / 60 / 60
# log_base_path = Path('/Volumes/Gandhi Lab - HT/Soyun/VR Logs')
# log_paths = list(log_base_path.glob('*/*.csv'))

class TrajectoryLog(object):
    def __init__(self, path):
        self.path = path.with_suffix('.npy')
        self.datetime = datetime.strptime(path.stem, 'VR%Y%m%d%H%M%S')
        try:
            self.frame = np.rec.array(np.load(self.path.str))
        except Exception as e:
            print 'First access to the log...convert!'
            self.frame = self.import_raw(path.with_suffix('.csv'))
    @classmethod
    def import_raw(cls, path): # csv
        filetime = datetime.strptime(path.stem, 'VR%Y%m%d%H%M%S')
        pos = np.rec.array(Position.from_lines(path.open()), names=Position._fields)
        velo = velocity.make(pos.ts, pos.x, pos.y)
        epochs = [
            time.mktime(
                (filetime + timedelta(seconds=delta)).timetuple()
            ) + (
                (filetime + timedelta(seconds=delta)).microsecond * 1e-6)
            # below is more correct way but for some reason Arduino timestamp does not respect daylight saving time.
            # ((filetime + timedelta(hours=offset, seconds=delta) - datetime(1970, 1, 1)).total_seconds()
            for delta in pos.ts]
        frame = np.rec.array(zip(*(
            epochs, pos.x, pos.y, pos.z, velo)
        ), names=['E', 'X', 'Y', 'Z', 'V'])
        np.save(path.with_suffix('.npy').str, frame)
        return frame
    @classmethod
    def query(cls, time):
        print 'Query a matching log file from datetime...', time
        root = manager.instance('opt').trajectory_root
        for path in reversed(sorted(root.rglob('VR*.csv'))):
            logtime = datetime.strptime(path.stem, 'VR%Y%m%d%H%M%S')
            if logtime < time:
                print 'Found one!', path.name
                return cls(path)
        else:
            raise Exception(
                'There is no matching log file with {}.'.format(time))
    def align(self, tss): # timestamps
        s, e = np.searchsorted(self.frame.E, [tss[0], tss[-1]], side='right')
        part = self.frame[s:e]
        if not part.size:
            return part
        return np.rec.array(
            map(tuple, signal.resample(part.tolist(), len(tss))),
            names=self.frame.dtype.names)

# qwe = datetime(2016, 3, 4, 9, 33, 35)
# test = Path('/Volumes/Users/ht/dev/current/pacu/tmp/Soyun/VR20160304093335.csv')
# q = TrajectoryLog(test)
# querytest = datetime.fromtimestamp(1457114437.12)
# one = TrajectoryLog.query(querytest)
# querydfail = datetime.fromtimestamp(1347114437.12)
# one = TrajectoryLog.query(querydfail)
