from __future__ import division

import numpy as np
from cStringIO import StringIO
from matplotlib import pyplot as plt

from pacu.util.prop.memoized import memoized_property
from pacu.core.io.scanimage.fit import tau
from pacu.core.io.scanimage import util

class DecayResponse(object):
    tau = None
    x = ()
    y_fit = ()
    orientation = ()
    def __init__(self, orientation):
        self.orientation = orientation
    def toDict(self):
        return util.nan_for_json(dict(
            traces = self.traces,
            mean = self.mean,
            name = self.orientation.value,
            tau = self.tau,
            x = self.x,
            y_fit = self.y_fit
        ))
    @classmethod
    def from_adaptor(cls, response, adaptor):
        self = cls(response.trace)
        self.orientation = response.orientations.responses[
            response.normalfit.max_orientation_index]
        try:
            c_value, self.x, self.y_fit = tau.fit(self.mean)
            self.tau = 1.0 / (adaptor.capture_frequency * c_value)
        except Exception as e:
            print 'Failed to get decay/tau fit: ' + str(e)
            self.tau = np.nan
        return self
    @memoized_property
    def traces(self):
        try:
            return np.vstack([trace.array for trace in self.orientation.offtimes])
        except Exception as e:
            print 'Decay response trace error', e
            return []
    @memoized_property
    def mean(self):
        return np.array(self.traces).mean(axis=0)
    def plot(self):
        io = StringIO()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('Decay at {}'.format(self.orientation.value))
        data = self.toDict()
        ax.plot(data.get('mean'), linewidth=1, color='red', label='mean')
        ax.plot(data.get('y_fit'), linewidth=1, color='blue', label='fit')
        for t in data.get('traces'):
            ax.plot(t, linewidth=0.5, color='silver')
        ax.axis('tight')
        ax.legend()
        fig.savefig(io, format='svg', bbox_inches='tight')
        fig.clf()
        plt.close(fig)
        return io.getvalue()
