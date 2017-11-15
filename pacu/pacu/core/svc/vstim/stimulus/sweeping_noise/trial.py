import numpy as np
from PIL import Image
from psychopy import event
from psychopy.core import CountdownTimer
from pacu.core.svc.impl.exc import UserAbortException

from psychopy import core

class Trial(object):
    def __init__(self, stimulus, condition, duration, interval):
        self.frameCount = 0
        self.stimulus = stimulus
        self.condition = {}
        self.interval = interval
        self.duration = duration
    def start(self):
        inst = self.stimulus.instance
        interval = self.interval
        flip = self.stimulus.window.flip
        flipped = self.stimulus.clock.flipped
        for frame in self.stimulus.movie:
            if event.getKeys('escape'):
                raise UserAbortException()
            interval.start()
            inst.image = Image.fromarray(frame)
            inst.draw()
            flip()
            flipped()
            interval.complete()
        # self.getTime = CountdownTimer(self.duration).getTime
        return self
    def __nonzero__(self):
        return False
        # if event.getKeys('escape'):
        #     self.stimulus.should_stop = True
        # return self.getTime() > 0
    def __enter__(self):
        pass
        # self.interval.start()
        # self.stimulus.update_phase(self)
    def __exit__(self, *args):
        pass
        # self.interval.complete()
        # self.frameCount += 1
# random_frame = np.random.randint(256, size=(960, 1440)).astype('uint8')
# img = Image.fromarray(random_frame)
