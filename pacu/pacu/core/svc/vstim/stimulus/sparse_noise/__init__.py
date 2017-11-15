from itertools import product

import numpy as np
from psychopy import event
from psychopy import core
from psychopy import misc
from psychopy.core import MonotonicClock

from pacu.ext.psychopy import logging
from pacu.util.prop.memoized import memoized_property
from pacu.core.svc.impl.exc import UserAbortException
from pacu.core.svc.impl.exc import ServiceRuntimeException
from pacu.core.svc.impl.resource import Resource
from pacu.core.svc.impl.component import Component

from pacu.core.svc.vstim.stimulus.position_tuple import PositionTuple
from pacu.core.svc.vstim.stimulus.size_tuple import SizeTuple
from pacu.core.svc.vstim.stimulus.size import Size
from pacu.core.svc.vstim.stimulus.square_factor import SquareFactor
from pacu.core.svc.vstim.stimulus.repetition import Repetition
from pacu.core.svc.vstim.stimulus.duration import OnDuration
from pacu.core.svc.vstim.stimulus.duration import OffDuration
from pacu.core.svc.vstim.stimulus.sparse_noise.condition import Condition
from pacu.core.svc.vstim.stimulus.sparse_noise.trial import Trial
from pacu.core.svc.vstim.stimulus.randomize import Randomize

class StimulusResource(Resource):
    should_stop = False
    def __enter__(self):
        from psychopy.visual import ImageStim # eats some time
        from psychopy.visual import TextStim
        event.clearEvents()
        win = self.window.instance
        self.textstim = TextStim(win, text='')
        # image texture index order is iamge[y, x]
        self.instance = ImageStim(win=win, units='deg', #, filpVert=True,
            pos=self.component.position,
            size=self.component.size) #misc.pix2deg(win.size, win.monitor)*2)
        try:
            self.interval = self.window.get_isi()
        except Exception as e:
            raise ServiceRuntimeException(
                'Could not acquire window object. Please try again')
        return self
    @memoized_property
    def trials(self):
        from psychopy.data import TrialHandler # eats some time
        sqf = self.component.square_factor
        self.image = np.zeros((sqf, sqf))
        conditions = [
            Condition(x, y, v) for x, y, v
            in product(range(sqf), range(sqf), [-1, 1])
        ]
        ts = [Trial(self, cond, self.component.on_duration, self.interval)
            for cond in conditions]
        return TrialHandler(ts,
            nReps=self.component.repetition,
            method=('random' if self.component.randomize else 'sequential')
        )
    @property
    def synced(self):
        self.clock.synchronize(self)
        return iter(self)
    def __iter__(self):
        trials = self.trials
        clock = self.clock.instance
        clock.reset()
        for trial in trials:
            self.update_trial(trial)
            logging.msg('Entering trial #%s...' % trials.thisN)
            trials.addData('on_time', clock.getTime())
            yield trial.start()
            trials.addData('off_time', clock.getTime())
            self.flip_blank()
            core.wait(self.component.off_duration)
            self.instance.opacity = 1.0
            if self.should_stop:
                logging.msg('UserAbortException raised!')
                raise UserAbortException()
    def update_trial(self, trial):
        cond = trial.condition
        self.image[cond.y, cond.x] = cond.v
        self.instance.image = self.image
        self.instance.draw()
        self.image[cond.y, cond.x] = 0
    # def update_phase(self, trial):
    #     now = trial.tick()
    #     self.instance.phase = np.mod(now * trial.condition.tf, 1)
    #     self.instance.draw()
    #     self.window.flip()
    def flip_text(self, text):
        self.textstim.setText(text)
        self.textstim.draw()
        self.window.flip()
    def flip_blank(self):
        self.instance.opacity = 0.0
        self.instance.draw()
        self.window.flip()

class SparseNoiseStimulus(Component):
    sui_icon = 'grid layout'
    package = __package__
    repetition = Repetition(1)
    position = PositionTuple([0.0, 0.0])
    square_factor = SquareFactor(8)
    size = Size(30)
    on_duration = OnDuration(1)
    off_duration = OffDuration(0.5)
    randomize = Randomize(True)
    __call__ = StimulusResource.bind('window', 'clock', 'projection')
