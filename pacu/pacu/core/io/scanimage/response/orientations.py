import numpy as np
from matplotlib import pyplot as plt
from cStringIO import StringIO

from pacu.util.prop.memoized import memoized_property
from pacu.core.io.scanimage.response.orientation import Orientation

class OrientationsResponse(object):
    capture_frequency = 6.1 # default
    def toDict(self):
        return self.data
    @classmethod
    def from_adaptor(cls, response, adaptor):
        self = cls()
        self.capture_frequency = adaptor.capture_frequency
        self.responses = [
            Orientation.from_adaptor(ori, response.trace, adaptor)
            for ori in adaptor.locator.orientations.loop()]
        return self
    @property
    def names(self):
        return [ori.value for ori in self.responses]
    @memoized_property
    def bss(self):
        return np.array([np.vstack(
            trace.array for trace in ori.baselines
        ) for ori in self.responses])
    @memoized_property
    def ons(self):
        return np.array([np.vstack(
            trace.array for trace in ori.ontimes
        ) for ori in self.responses])
    @property
    def data(self):
        bss_ons = np.concatenate([
            self.bss, self.ons
        ], axis=2).transpose(1, 0, 2) #.reshape((8, 360))
        n_rep, n_ori, n_frm = bss_ons.shape
        traces = bss_ons.reshape((n_rep, n_ori*n_frm))
        return dict(traces=traces,
            mean=traces.mean(axis=0),
            indices=self.orientation_indices(n_frm/2))
    def orientation_indices(self, n_frames):
        return {int((index*2 + 1.5)*n_frames): ori.value
            for index, ori in enumerate(self.responses)}
    @property
    def windowed_ontimes(self):
        return np.array([
            ori.windowed_mean_for_ontimes
            for ori in self.responses])
    @property
    def regular_ontimes(self):
        return np.array([
            ori.regular_mean_for_ontimes
            for ori in self.responses])
    def plot(self):
        io = StringIO()
        fig = plt.figure(figsize=(16, 9))
        ax = fig.add_subplot(111)
        ax.set_title('Orientation of Stimulus')
        data = self.data
        for t in data.get('traces'):
            ax.plot(t, linewidth=0.5, color='silver')
        ax.plot(data.get('mean'), linewidth=1, color='red', label='mean')
        ax.axis('tight')
        ax.legend()
        fig.savefig(io, format='svg', bbox_inches='tight')
        fig.clf()
        plt.close(fig)
        return io.getvalue()
