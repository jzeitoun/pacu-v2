
from psychopy import core
from pacu.ext.psychopy import logging
from pacu.core.svc.impl.resource import Resource
from pacu.core.svc.impl.component import Component
from pacu.core.svc.vstim.clock.wait_time import WaitTime

class ClockResource(Resource):
    def __enter__(self):
        clock = core.Clock()
        logging.setDefaultClock(clock)
        self.started_at = clock.getTime()
        self.instance = clock
        return self
    def getTime(self):
        return self.instance.getTime()
    def __exit__(self, type, value, traceback):
        self.finished_at = self.instance.getTime()
    def wait(self, stimulus):
        wtime = self.component.wait_time
        logging.msg('Clock synchronized. Session starts after %s sec(s)...' % wtime)
        logging.flush()
        for countdown in reversed(range(wtime)):
            stimulus.flip_text(
                'Clock synchronized.\nSession starting in %s...' % (countdown+1))
            core.wait(1)
    def synchronize(self, stimulus):
        self.wait(stimulus)
    # this method should do nothing without obvious resaon.
    # refer pacu/core/svc/vstim/clock/labjack/driver.py 
    def reset(self):
        self.instance.reset()
    def flipped(self):
        pass
class ClockBase(Component):
    wait_time = WaitTime(0)
    __call__ = ClockResource.bind()
