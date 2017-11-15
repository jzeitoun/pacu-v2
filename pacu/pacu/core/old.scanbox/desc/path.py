from pacu.util.path import Path
from pacu.util.descriptor.mixin.memoization import MemoMix

class PathDescriptor(MemoMix):
    __by_func__ = Path
