from pacu.core.svc.vstim.clock.base import ClockResource
from pacu.core.svc.vstim.clock.base import ClockBase

class InternalClock(ClockBase):
    sui_icon = 'wait'
    package = __package__
    __call__ = ClockResource.bind()
