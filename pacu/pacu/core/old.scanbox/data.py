from pacu.util import identity
from pacu.util.path import Path
from pacu.util.prop.memoized import memoized_property
from pacu.core.service.analysis.mapper.scanbox import adapter
from pacu.profile import manager

path_manager = manager.get('path')

class ScanboxData(object):
    meta = None
    data = None
    def __init__(self, matpath):
        self.matpath = matpath
    @property
    def is_available(self):
        try: # literally existence check
            return self.meta is not None and self.data is not None
        except Exception as e:
            return False
    @memoized_property
    def meta(self):
        return adapter.get_meta(self.matpath)
    @memoized_property
    def data(self):
        return self.meta.raw.memmap
    @classmethod
    def populate(cls, path=None):
        path = Path(path) if path else path_manager.instance().scanbox_root
        paths = path.rglob('*.mat')
        data_set = [(path.name, cls(path.str)) for path in paths]
        return [(name, vars(self))
                for name, self in data_set if self.is_available]

# mat = '/Volumes/Users/ht/tmp/pysbx-data/JZ6/JZ6_000_003.mat'
# sd = ScanboxData(mat)
# sd.is_available
# q = ScanboxData.populate('/Volumes/Users/ht/tmp/pysbx-data')
