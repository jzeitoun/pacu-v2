from collections import namedtuple

import numpy as np

from pacu.util.prop.memoized import memoized_property
from pacu.core.io.scanimage.locator.impl import Locator
from pacu.core.io.scanimage.adaptor.indice import ScanimageIndiceAdaptor

Frame = namedtuple('Frame', 'duration interval ontimes baseline')

class ScanimageDBAdaptor(object):
    def __init__(self, rec):
        self.rec = rec
    @property
    def sfrequencies(self):
        return self.rec.spatial_frequencies
    @property
    def tfrequencies(self):
        return [float(self.rec.temporal_frequencies)]
    @property
    def orientations(self):
        return self.rec.orientations
    @property
    def sequence(self):
        return self.rec.sequence
    @property
    def capture_frequency(self):
        return self.rec.captureFrequency
    @property
    def n_conditions(self):
        return self.rec.nConditions
    @memoized_property
    def locator(self):
        return Locator.from_one_based_sequence(self.sequence,
            self.sfrequencies, self.tfrequencies, self.orientations,
            self.rec.blankOn, self.rec.flickerOn)
    @memoized_property
    def frame(self):
        return Frame(
            np.round(self.rec.duration_F).astype(int),
            np.round(self.rec.waitinterval_F).astype(int),
            np.round(self.rec.ontimes_F).astype(int),
            # below may not be used any more.
            # see `pacu.core.io.scanimage.trace.base` and
            # `pacu.core.io.scanimage.response.orientation`.
            int(1.5*self.capture_frequency))
    @property
    def indice(self):
        return ScanimageIndiceAdaptor(self)
