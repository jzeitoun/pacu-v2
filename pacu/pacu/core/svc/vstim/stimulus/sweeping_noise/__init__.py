from __future__ import division

import numpy as np
from PIL import Image
from psychopy import core
from psychopy import misc

# eats some time
from psychopy.data import TrialHandler
from psychopy.visual import TextStim
from psychopy.visual import ImageStim

from pacu.ext.psychopy import logging
from pacu.util.prop.memoized import memoized_property
from pacu.core.svc.impl.resource import Resource
from pacu.core.svc.impl.component import Component
from pacu.core.svc.vstim.stimulus.duration import OnDuration
from pacu.core.svc.vstim.stimulus.contrast import Contrast
from pacu.core.svc.vstim.stimulus.sfrequencies import SFrequencies
from pacu.core.svc.vstim.stimulus.tfrequencies import TFrequencies
# from pacu.core.svc.vstim.stimulus.sweeping_noise import postprocess
from pacu.core.svc.vstim.stimulus.sweeping_noise.trial import Trial
from pacu.core.svc.vstim.stimulus.sweeping_noise.generator import SweepingNoiseGenerator

from pacu.core.svc.vstim.stimulus.snp_max_spat_freq import SNPMaxSFrequency
from pacu.core.svc.vstim.stimulus.snp_max_temp_freq import SNPMaxTFrequency
from pacu.core.svc.vstim.stimulus.snp_contrast import SNPContrast
from pacu.core.svc.vstim.stimulus.snp_rotation import SNPRotation
from pacu.core.svc.vstim.stimulus.snp_filter import SNPFilter
from pacu.core.svc.vstim.stimulus.snp_duration import SNPDuration
from pacu.core.svc.vstim.stimulus.snp_bandwidth import SNPBandwidth
from pacu.core.svc.vstim.stimulus.snp_image_mag import SNPImageMag
from pacu.core.svc.vstim.stimulus.snp_img_size import SNPImgSize
from pacu.core.svc.vstim.stimulus.snp_view_width import SNPViewWidth
from pacu.core.svc.vstim.stimulus.snp_contr_period import SNPContrPeriod
from pacu.core.svc.vstim.stimulus.snp_view_port_override import SNPViewPortOverride
from pacu.core.svc.vstim.stimulus.snp_cont_thresh import SNPContrThreshold

from ipdb import set_trace

class StimulusResource(Resource):
    should_stop = False
    def __enter__(self):
        win = self.window.instance
        proj = self.projection.instance
        try:
            eyepoint_x = proj.eyepoint[0]
        except:
            eyepoint_x = 0.5
        self.textstim = TextStim(win, text='')

        size_overriden = self.component.snp_viewport_override
        view_size = size_overriden if any(size_overriden) else win.size
        win_x, win_y = win.size
        view_x, view_y = view_size
        afr = 30 # int(win.getActualFrameRate() * 0.5)
        logging.msg('Fixed frame rate: ' + str(afr))
        self.flip_text('Generating stimulus...it may take a few minutes.')
        try:
            logging.msg('init movie...')
            print 'init movie...'
            width, height = win.monitor.getSizePix()
            mgen = SweepingNoiseGenerator(
                max_spat_freq = self.component.snp_max_spat_freq,
                max_temp_freq = self.component.snp_max_temp_freq,
                contrast = self.component.snp_contrast,
                rotation = self.component.snp_rotation,
                bandfilter = self.component.snp_filter,
                duration = self.component.snp_duration,
                bandwidth = self.component.snp_bandwidth,
                viewwidth = self.component.snp_view_width,
                imsize = self.component.snp_img_size,
                binary_threshold = self.component.snp_cont_thresh,
                framerate=afr,
                contr_period=self.component.snp_contr_period,
                screenWidthPix = win_x,
                screenHeightPix = win_y,
                viewport_x = view_x,
                viewport_y = view_y,
                screenWidthCm = self.window.monitor.component.width,
                screenHeightCm = self.window.monitor.component.height,
                screenDistanceCm = self.window.monitor.component.dist,
                eyepoint_x = eyepoint_x
            )
        except Exception as e:
            print 'got exception', type(e)
            print e
        else:
            print 'generating...'
            mgen.generate()
            print 'rotating...'
            mgen.rotate()
            print 'viewmasking...'
            mgen.viewmask()
            # print 'croping...'
            # mgen.crop()
            print 'done!'
            self.movie = mgen.moviedata
            print 'shape is', self.movie.shape

            logging.msg('masking window...')
            print 'masking window...'
            # Setting viewport width
            # screenWidthCm = self.window.monitor.component.width
            # screenDistanceCm = self.window.monitor.component.dist

            self.flip_text('Generating stimulus...done!')

        logging.msg('creating image stim...')
        print 'creating image stim...'
        # imagebuffer to play each frame
        self.instance = ImageStim(
            win = win,
            # size = [1440, 900], # prevent stretch
            # size = [900, 900], # for mbpr with 10cm
            size = view_size,
            units = 'pix',
            interpolate = True
        )
        logging.msg('ImageStim size: ' + str(self.instance.size))
        try:
            logging.msg('getting ISI...')
            self.interval = self.window.get_isi()
        except Exception as e:
            raise ServiceRuntimeException(
                'Could not acquire window object. Please try again')
        return self
    @memoized_property
    def trials(self):
        ts = [Trial(self, cond, self.component.snp_duration, self.interval)
            for cond in [self.movie]]
        return TrialHandler(ts, nReps=1, method='random')
    @property
    def synced(self):
        self.clock.synchronize(self)
        return iter(self)
    def __iter__(self):
        for trial in self.trials:
            index = self.trials.thisN
            logging.msg('Entering trial #%s...' % index)
            # self.update_trial(trial)
            # self.trials.addData('on_time', self.clock.getTime())
            yield trial.start()
            # self.trials.addData('off_time', self.clock.getTime())
            self.flip_blank()
    def update_trial(self, trial):
        pass
    def update_phase(self, trial):
        pass
    def flip_text(self, text):
        self.textstim.setText(text)
        self.textstim.draw()
        self.window.flip()
    def flip_blank(self):
        self.instance.opacity = 0.0
        self.instance.draw()
        self.window.flip()
    def __exit__(self, type, value, tb):
        self.movie = None
        return super(StimulusResource, self).__exit__(type, value, tb)
class SweepingNoiseStimulus(Component):
    sui_icon = 'share alternate'
    package = __package__
    off_duration = 0
    __call__ = StimulusResource.bind('window', 'clock', 'projection')
    snp_max_spat_freq = SNPMaxSFrequency(0.5)
    snp_max_temp_freq = SNPMaxTFrequency(5)
    snp_contrast = SNPContrast(0.5)
    snp_rotation = SNPRotation('0')
    snp_filter = SNPFilter('Square')
    snp_duration = SNPDuration(300)
    snp_bandwidth = SNPBandwidth(20)
    snp_img_size = SNPImgSize(128)
    snp_view_width = SNPViewWidth(0)
    snp_contr_period = SNPContrPeriod(10)
    snp_viewport_override = SNPViewPortOverride([1080, 1000])
    snp_cont_thresh = SNPContrThreshold(50)
