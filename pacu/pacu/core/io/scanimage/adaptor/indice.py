from collections import namedtuple

import numpy as np

Indices = namedtuple('Indices', 'first last')

class ScanimageIndiceAdaptor(object):
    def __init__(self, adaptor):
        self.adaptor = adaptor
    @property
    def ontimes(self):
        first_frames = np.array(
            self.adaptor.locator.map_condition_indice_from(self.adaptor.frame.ontimes))
        last_frames = first_frames + self.adaptor.frame.duration
        return Indices(first_frames, last_frames)
    @property
    def baselines(self):
        ontime_first_frames = self.ontimes.first
        first_frames = ontime_first_frames - self.adaptor.frame.interval
        if (first_frames < 0).sum():
            print("Error: The first pre-stimulus blank isn't long enough. "
                "This could make some side effect on the analysis.")
            first_frames[:] = 0
        last_frames = ontime_first_frames - 1
        return Indices(first_frames, last_frames)
    @property
    def offtimes(self):
        first_frames = self.ontimes.last
        natural_indice = np.array(
            self.adaptor.locator.arg_condition_indice
        ) != self.adaptor.locator.arg_last_sequence
        first_frames[natural_indice] += 1
        last_frames = first_frames + self.adaptor.frame.interval
        return Indices(first_frames, last_frames)




