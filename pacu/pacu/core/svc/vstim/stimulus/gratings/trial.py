from psychopy import event
from psychopy.core import CountdownTimer

class Trial(object):
    def __init__(self, stimulus, condition, duration, interval):
        self.stimulus = stimulus
        self.condition = condition
        self.interval = interval
        self.duration = duration
    def tick(self):
        return self.duration - self.getTime()
    def start(self):
        self.getTime = CountdownTimer(self.duration).getTime
        return self
    def __nonzero__(self): # used in while statement as an ISI
        if event.getKeys('escape'):
            self.stimulus.should_stop = True
        return self.getTime() > 0
    def __enter__(self):
        self.interval.start()
        self.stimulus.update_phase(self)
    def __exit__(self, *args):
        self.interval.complete()
