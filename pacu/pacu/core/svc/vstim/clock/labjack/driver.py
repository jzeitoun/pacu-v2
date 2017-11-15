from pacu.ext.labjack.u3 import U3Trigger
from pacu.ext.psychopy import logging
from pacu.core.svc.impl.exc import TimeoutException
from pacu.core.svc.impl.exc import UserAbortException
from pacu.core.svc.impl.exc import ComponentNotFoundError
from pacu.core.svc.vstim.clock.timeout import Timeout
from pacu.core.svc.vstim.clock.base import ClockResource
from pacu.core.svc.vstim.clock.base import ClockBase
from pacu.core.svc.vstim.clock.wait_time import WaitTime
from pacu.core.svc.vstim.clock.pin import Pin
from psychopy import event
from psychopy.core import CountdownTimer

import time

class LabJackDriverResource(ClockResource):
    def __enter__(self):
        try:
            self.trigger = U3Trigger()
            self.trigger.__enter__()
            self.fire = self.trigger.fire
            self.pin = self.component.pin
        except Exception as e:
            raise ComponentNotFoundError(
                'Could not initialize LabJack Device: ' + str(e))
        return super(LabJackDriverResource, self).__enter__()
    def __exit__(self, type, value, tb):
        self.trigger.__exit__(type, value, tb)
        return super(LabJackDriverResource, self).__exit__(type, value, tb)
        # self.proxy.__exit__(type, value, traceback)
    # this is ugly special magic method
    # for sweeping noise this time, entire stimulus is running at
    # just one initial trials so there is no way to comply with __enter__
    # and __exit__ in trial class. In stead of this,
    # the loop in `start` method of trial.py will call
    # this method in every flipping so that this driver catch
    # the frame change.
    def flipped(self):
        self.fire(self.pin)

class LabJackDriver(ClockBase):
    sui_icon = 'lightning'
    package = __package__
    wait_time = WaitTime(5)
    pin = Pin(0)
    __call__ = LabJackDriverResource.bind()
    description = (
        'This clock is supposed to drive external device '
        'along with sequence of internal stimulus. Most of the time, '
        'clock is setup to be controlled from external signals coming '
        'in so that the stimulus can go synchronized, but this clock '
        'works in the opposite way. Designed to work with Andor devices.')
