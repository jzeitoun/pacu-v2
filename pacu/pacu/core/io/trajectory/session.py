import shutil

from pacu.util.path import Path
from pacu.util.inspect import repr
from pacu.util.prop.memoized import memoized_property
from pacu.core.io.scanimage.nmspc import HybridNamespace

class TrajectorySession(object):
    roi = None
    opt = None
    __repr__ = repr.auto_strict
    def __init__(self, path):
        self.path = Path(path).with_suffix('.session')
        self.roi = HybridNamespace.from_path(self.path.joinpath('roi'))
        self.opt = HybridNamespace.from_path(self.path.joinpath('opt'))
    def toDict(self):
        return dict(name=self.path.stem, path=self.path.str)
    @property
    def exists(self):
        return self.path.is_dir()
    def create(self):
        self.path.mkdir()
    def remove(self):
        shutil.rmtree(self.path.str)
    # @memoized_property
    # def trials(self):
    #     return [
    #         TrajectoryTrial(path.with_name(path.stem))
    #         for path in sorted(self.path.ls('*.imported'))]
    # def get_trial(self, id):
    #     path = sorted(self.path.ls('*.imported'))[id]
    #     return TrajectoryTrial(path.with_name(path.stem))
