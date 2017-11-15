import numpy as np

from pacu.util.path import Path

class NoRawDataError(Exception): pass
class RawDataParseError(Exception): pass

def find_nth_rising(array, occur=4, state=0):
    for index, e in enumerate(array):
        if e != state:
            state = e
            if e == 1:
                occur -= 1
            if occur == 0:
                return index
    else:
        raise

def import_ephys(filepath):
    """
    filepath = '/Volumes/Users/ht/dev/current/pacu/tmp/Jack/jzg1/day1/day1_000_007.txt'
    risings = import_ephys(filepath)
    """
    path = Path(filepath)
    if not path.is_file():
        raise NoRawDataError('Can not find raw data {!r}'.format(path.name))
    try:
        raw = np.genfromtxt(path.str, delimiter=' ', names=['TTL', 'ON'], dtype='b')
        first_frame = find_nth_rising(raw['TTL'])
        data = raw[first_frame:]
        data['ON'][data['ON'] == 60] = 1
        edges = np.diff(data['TTL']) > 0
        ed_indices = np.where(edges)[0] + 1
        on_chunks = np.split(data['ON'], ed_indices)
        return np.array([chunk.any() for chunk in on_chunks])
    except Exception as e:
        raise RawDataParseError(e)

# filepath = '/Volumes/Users/ht/dev/current/pacu/tmp/Jack/jzg1/day1/day1_000_007.txt'
# risings = import_ephys(filepath)

class ScanboxEphysView(object):
    def __init__(self, io, path):
        self.io = io
        self.path = Path(path).with_suffix('.txt')
        self.npy = self.path.with_suffix('.io').joinpath('ephys.npy')
    @property
    def trace(self):
        return np.load(self.npy.str).tolist() if self.npy.is_file() else []
    def toDict(self):
        return dict(
            trace = self.trace
        )
    def reimport(self):
        print 'Importing ephys data. This may take a few minutes.'
        np.save(self.npy.str, import_ephys(self.path))
        print 'Import Success!'
        return self.toDict()
    def remove(self):
        self.npy.unlink()
        return self.toDict()
