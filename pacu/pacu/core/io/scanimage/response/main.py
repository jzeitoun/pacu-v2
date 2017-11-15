from pacu.core.io.scanimage.response.base import BaseResponse
from pacu.core.io.scanimage.response.overview import OverviewResponse

class MainResponse(BaseResponse):
    @classmethod
    def from_adaptor(cls, trace, adaptor):
        self = cls(trace)
        self.overview = OverviewResponse.from_adaptor(self, adaptor)
        return self
    def toDict(self):
        return dict(overview=self.overview)
