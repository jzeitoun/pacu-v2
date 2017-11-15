from __future__ import division

from itertools import product

import numpy as np
from scipy import signal
from psychopy import core
from psychopy import misc
from psychopy import event
from psychopy.core import MonotonicClock

from pacu.ext.psychopy import logging
from pacu.util.prop.memoized import memoized_property
from pacu.core.svc.impl.exc import UserAbortException
from pacu.core.svc.impl.exc import ServiceRuntimeException
from pacu.core.svc.impl.resource import Resource
from pacu.core.svc.impl.component import Component
from pacu.core.svc.vstim.stimulus.base import StimulusBase
from pacu.core.svc.vstim.stimulus.orientation import Orientation
from pacu.core.svc.vstim.stimulus.sfrequency import SFrequency
from pacu.core.svc.vstim.stimulus.max_contrast import MaxContrast
from pacu.core.svc.vstim.stimulus.tfrequency import TFrequency
from pacu.core.svc.vstim.stimulus.width import Width
from pacu.core.svc.vstim.stimulus.duration import OnDuration
from pacu.core.svc.vstim.stimulus.contrast_period import ContrastPeriod
from pacu.core.svc.vstim.stimulus.opacity_period import OpacityPeriod
from pacu.core.svc.vstim.stimulus.gratings.condition import RevContModCondition
from pacu.core.svc.vstim.stimulus.gratings.trial import Trial

# Reverse Contrast Modulating Stim

class StimulusResource(Resource):
    should_stop = False
    def __enter__(self):
        from psychopy.visual import GratingStim # eats some time
        from psychopy.visual import TextStim
        win = self.window.instance
        self.textstim = TextStim(win, text='')
        # for some reason x, y were swapped..
        # this may happen if monitor setup was portrait mode instead of landscape.
        width, height = misc.pix2deg(win.size, win.monitor)
        if self.component.width:
            width = self.component.width
        self.instance = GratingStim(win=win, tex='sin',
            units='deg',
            size = (height, width)
            # size = misc.pix2deg(win.size, win.monitor)
        )
        tf = self.component.tfrequency
        self.contrast_factor = tf*np.pi*(2/self.component.ct_period)
        self.opacity_factor = tf*np.pi*(2/self.component.op_period)
        try:
            self.interval = self.window.get_isi()
        except Exception as e:
            raise ServiceRuntimeException(
                'Could not acquire window object. Please try again')
        return self
    @memoized_property
    def trials(self):
        from psychopy.data import TrialHandler # eats some time
        conditions = [RevContModCondition(
            self.component.orientation,
            self.component.sfrequency,
            self.component.tfrequency,
        )]
        ts = [Trial(self, cond, self.component.on_duration, self.interval)
            for cond in conditions]
        return TrialHandler(ts,
            nReps=1, method='random')
    @property
    def synced(self):
        self.clock.synchronize(self)
        return iter(self)
    def __iter__(self):
        for trial in self.trials:
            index = self.trials.thisN
            logging.msg('Entering trial #%s...' % index)
            self.update_trial(trial)
            self.trials.addData('on_time', self.clock.getTime())
            yield trial.start()
            self.trials.addData('off_time', self.clock.getTime())
            self.flip_blank()
            # core.wait(self.component.off_duration)
            self.instance.opacity = 1.0
    def update_trial(self, trial):
        self.instance.ori = trial.condition.ori
        self.instance.sf = trial.condition.sf
        self.instance.tf = trial.condition.tf
    def update_phase(self, trial):
        if self.should_stop:
            logging.msg('UserAbortException raised!')
            raise UserAbortException()

        now = trial.tick()
        cont = np.sin(now*self.contrast_factor)
        opa = np.cos(now*self.opacity_factor)

        self.instance.contrast = signal.square(cont)
        opacity = (opa + 1) / 2
        max_contrast = self.component.max_contrast
        opacity = min(opacity, max_contrast)
        self.instance.opacity = opacity

        self.instance.draw()
        self.window.flip()
        self.clock.flipped()
    def flip_text(self, text):
        self.textstim.setText(text)
        self.textstim.draw()
        self.window.flip()
    def flip_blank(self):
        self.instance.opacity = 0.0
        self.instance.draw()
        self.window.flip()

class RevContModGratingsStimulus(Component):
    sui_icon = 'align justify'
    package = __package__
    orientation = 270 # Orientation(270)
    sfrequency = SFrequency(0.05)
    tfrequency = TFrequency(1)
    on_duration = OnDuration(300)
    ct_period = ContrastPeriod(1)
    op_period = OpacityPeriod(10)
    max_contrast = MaxContrast(1.0)
    width = Width(0)
    __call__ = StimulusResource.bind('window', 'clock', 'projection')
