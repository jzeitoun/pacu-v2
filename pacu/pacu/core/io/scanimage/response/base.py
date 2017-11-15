from scipy import stats
from matplotlib import pyplot as plt
from cStringIO import StringIO

from pacu.core.io.scanimage import util
from pacu.core.io.scanimage.response.overview import OverviewResponse
from pacu.core.io.scanimage.response.orientations import OrientationsResponse
from pacu.core.io.scanimage.response.normalfit import NormalfitResponse
from pacu.core.io.scanimage.response.decay import DecayResponse
from pacu.core.io.scanimage.response.bootstrap import BootstrapResponse

class BaseResponse(object):
    sfreq = None
    overview = None
    orientations = None
    normalfit = None
    decay = None
    stats = None
    comment = None
    blank = None
    flicker = None
    anova = None
    bootstrap = None
    sog_initial_guess = None
    def __init__(self, trace):
        self.trace = trace
    @classmethod
    def from_adaptor(cls, roi, trace, adaptor):
        self = cls(trace)
        self.blank = roi.blank
        self.flicker = roi.flicker
        self.sfreq = adaptor.locator.sfrequencies.current
        self.overview = OverviewResponse.from_adaptor(self, adaptor)
        self.orientations = OrientationsResponse.from_adaptor(self, adaptor)
        return self
    def toDict(self):
        try:
            return dict(
                sfreq = self.sfreq,
                overview = self.overview,
                orientations = self.orientations,
                bootstrap = self.bootstrap,
                fit = self.normalfit,
                decay = self.decay,
                stats = self.stats,
                sog_initial_guess = self.sog_initial_guess)
        except AttributeError as e:
            return dict(error=str(e))
        except Exception as e:
            return dict(error=str(e))
    def update_fit_and_decay(self, roi, adaptor, initial_guess=None, heavy=False):
        if initial_guess:
            self.sog_initial_guess = initial_guess
        self.normalfit = NormalfitResponse.from_adaptor(
            self, adaptor, roi.best_o_pref)
        self.decay = DecayResponse.from_adaptor(self, adaptor)
    def plot(self):
        io = StringIO()
        fig = plt.figure(figsize=(16, 9))
        ax = fig.add_subplot(111)
        ax.plot(self.trace, linewidth=0.5)
        ax.set_title('Response')
        ax.axis('tight')
        fig.savefig(io, format='svg', bbox_inches='tight')
        fig.clf()
        plt.close(fig)
        return io.getvalue()
