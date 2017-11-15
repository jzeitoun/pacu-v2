from pacu.ext.labjack.u3 import U3Trigger
from pacu.core.svc.impl.exc import ComponentNotFoundError
from pacu.core.svc.vstim.clock.base import ClockResource
from pacu.core.svc.vstim.clock.base import ClockBase
from pacu.core.svc.vstim.clock.wait_time import WaitTime
from pacu.core.svc.vstim.clock.pin import Pin

import time

class LabJackMiniscopeDriverResource(ClockResource): # will use psychopy clock for visstim timestamps
    def __enter__(self):
        try:
            self.trigger = U3Trigger()
            self.trigger.__enter__()
            self.fire = self.trigger.fire
            self.pin = self.component.pin
        except Exception as e:
            raise ComponentNotFoundError(
                'Could not initialize LabJack Device: ' + str(e))
        return super(LabJackMiniscopeDriverResource, self).__enter__()
    def __exit__(self, type, value, tb):
        self.trigger.instance.setFIOState(self.pin, 0)
        self.trigger.__exit__(type, value, tb)
        return super(LabJackMiniscopeDriverResource, self).__exit__(type, value, tb)
    def synchronize(self, stimulus):
        self.wait(stimulus)
        self.trigger.instance.setFIOState(self.pin, 1)

class LabJackMiniscopeDriver(ClockBase):
    sui_icon = 'lightning'
    package = __package__
    wait_time = WaitTime(5)
    pin = Pin(0)
    __call__ = LabJackMiniscopeDriverResource.bind()
    description = (
        'This clock is supposed to drive Miniscope '
        'by using LabJack.')
