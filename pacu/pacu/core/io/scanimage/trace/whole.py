from pacu.core.io.scanimage.trace.base import BaseTrace
from pacu.core.io.scanimage.trace.sliced import SlicedTrace

class WholeTrace(BaseTrace):
    def __init__(self, array):
        self.array = array
        self.end = len(array)
    def zip_slice(self, indices):
        starts, ends = indices
        return SlicedTrace.by_zip_slice(self.array, starts, ends)
