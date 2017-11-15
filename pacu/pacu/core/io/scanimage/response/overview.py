class OverviewResponse(object):
    def __init__(self, array):
        self.array = array
    def toDict(self):
        return dict(array=self.array)
    @classmethod
    def from_adaptor(cls, response, adaptor):
        self = cls(response.trace)
        return self
