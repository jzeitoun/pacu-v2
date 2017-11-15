import time

from pacu.core.svc.analysis.i3d.twoway.base import TwowayBase

class TwowayROI(TwowayBase):
    def __init__(self, polygon=None, rid=None, active=None, **kwargs):
        self.active = bool(active)
        self.polygon = polygon or []
        self.rid = rid or 'roi.{}'.format(time.time())
