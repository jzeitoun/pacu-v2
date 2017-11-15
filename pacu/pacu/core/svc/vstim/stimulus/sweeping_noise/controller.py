from collections import namedtuple
from PIL import Image
from psychopy import misc
from psychopy import event
from psychopy.core import StaticPeriod

from pacu.core.service.property import DependencySpec
from pacu.core.service.vstim.stimulus.trial import Trial
from pacu.core.service.exc import UserAbortException
from pacu.core.service.spec import Spec
from pacu.core.service.property import IntSpec
from pacu.core.service.property import FloatSpec
from pacu.core.service.vstim.stimulus import sweeping_noise_gen as sng
from pacu.core.service.validator import is_positive
# deprecated?
# deprecated?
# deprecated?
# deprecated?
class SweepingNoiseStimulus(Spec):
    """
    Sweeping noise. For now, the texture is supposed to
    take whole resolution of monitor. So windowed (not fullscreen)
    stimulus is not recommended.
    """
    sui_icon = 'share alternate'
    monitor = DependencySpec('monitor')
    window = DependencySpec('window')
    duration = IntSpec(5, validator=is_positive)
    tex_size = IntSpec(64, validator=is_positive)
    contrast = FloatSpec(0.25, validator=is_positive)
    def get_instance(self):
        from psychopy.visual import ImageStim # eats some time
        return ImageStim(
            win   = self.window,
            image = Image.new('L', (self.tex_size, self.tex_size)),
            # units = 'pix',
            # size  = self.monitor.getSizePix(),
            units = 'deg',
            size  = misc.pix2deg(self.window.size, self.window.monitor)*2,
        )
    @property
    def conditions(self):
        Condition = namedtuple('Condition', '')
        return [Condition()]
    @property
    def trials(self):
        from psychopy.data import TrialHandler # eats some time
        trials = TrialHandler(map(Trial, self.conditions),
            nReps=1, method='random')
        trials.on_duration = 1
        trials.off_duration = 0
        return trials
    def __enter__(self):
        x, y = self.monitor.getSizePix()
        self.afr = self.window.getActualFrameRate() / 2
        self.mspf = self.window.getMsPerFrame()[0] * 2 / 1000.0
        self.movie = sng.SweepingNoiseGenerator().stim_to_movie(
            duration=self.duration,
            framerate=self.afr,
            imsize=self.tex_size,
            pixel_x=x,
            pixel_y=y,
            contrast = self.contrast
        )
        return self.trials
    def __exit__(self, type, value, traceback):
        if isinstance(value, UserAbortException):
            return True # which is OK.
    def show_blank(self, duration):
        pass
    def show_phased(self, phase):
        isi = StaticPeriod(screenHz=self.afr, win=self.window)
        for frame in self.movie:
            if event.getKeys('escape'):
                raise UserAbortException()
            isi.start(self.mspf)
            self.instance.image = Image.fromarray(frame)
            self.instance.draw()
            self.window.flip()
            isi.complete()
    def update_condition(self, condition):
        pass

# from psychopy import visual, core
# import numpy as np
# 
# def checkerboard():
#     tex = np.array([[1,-1],[-1,1]])
#     cycles=4
#     win = visual.Window([400,400])
#     stim = visual.PatchStim(win, tex=tex, size=128, units='pix',
#         sf=cycles/128.0, interpolate=False)
#     for i in range(100):
#         stim.phase = float(i)/float(100)
#         stim.draw()
#         win.flip()
#         core.wait(0.01)
