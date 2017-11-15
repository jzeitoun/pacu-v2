from pacu.core.io.scanimage.trace.base import BaseTrace

class SlicedTrace(BaseTrace):
    def __init__(self, array):
        self.array = array
    @classmethod
    def by_slice(cls, array, start, end):
        self = cls(array[start:end])
        self.start = start
        self.end = end
        return self
    @classmethod
    def by_slice_indices(cls, array, indices):
        return [cls.by_slice(array, first, last) for first, last in indices]
    @classmethod
    def by_zip_slice(cls, array, starts, ends):
        return cls.by_slice_indices(array, zip(starts, ends))
    def toDict(self):
        return dict(array=self.array, start=int(self.start), end=int(self.end))
