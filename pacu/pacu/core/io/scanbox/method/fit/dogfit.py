import base64
from collections import namedtuple
from scipy import optimize
from scipy import interpolate

# prevent trying to stream figure through X11
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt
from cStringIO import StringIO
import numpy as np
import random

from pacu.core.io.scanimage import util

# print 'svg fonttype', plt.rcParams['svg.fonttype']
plt.rcParams['svg.fonttype'] = 'path'
# print 'change to none'

#svg.fonttype : 'path'         # How to handle SVG fonts:
#    'none': Assume fonts are installed on the machine where the SVG will be viewed.
#    'path': Embed characters as paths -- supported by most SVG renderers
#    'svgfont': Embed characters as SVG fonts -- supported only by Chrome,
#               Opera and Safari

Stretched = namedtuple('Stretched', 'x y')
DogParam = namedtuple('DogParam', 'amp1 sig1 amp2 sig2')
Point = namedtuple('Point', 'x y')

TWOPI = np.pi * 2

class SpatialFrequencyDogFit(object):
    ballpark_dog = [(1, 20), (1, 80), (1, 10), (1, 80)]
    visual_field = np.linspace(-50, 50, 200) # in degrees in visual angle
    _dog_param = None # for memoization
    def __init__(self, rmax, fff, blank=None):
        self.flicker = fff or 0
        self.blank = blank
        xfreq, ymeas = zip(*([(0.0, fff)] + rmax))
        self.xfreq = np.array(xfreq)
        self.ymeas = np.array(ymeas)
        self.stretched = self.stretch()
        self.xstim = np.array(map(self.stimulus, self.stretched.x))
        # negative visual field squared
        self.nvfs = -np.square(self.visual_field)
    def stretch(self, n=1000):
        func = interpolate.interp1d(self.xfreq, self.ymeas)
        stretched = np.linspace(self.lowest_freq, self.highest_freq, n)
        return Stretched(stretched, func(stretched))
    def stimulus(self, sfreq):
        return np.cos(self.visual_field*TWOPI*sfreq)
    @property
    def lowest_freq(self):
        return self.xfreq[0]
    @property
    def highest_freq(self):
        return self.xfreq[-1]
    def ballpark_residuals_dog(self, params):
        err = self.stretched.y - self.response_dog_bulk(params)
        return np.square(err).sum()
    def lsq_residuals_dog(self, params):
        err = self.stretched.y - self.response_dog_bulk(params)
        np.square(err, err) # in-place
        err[0] = err[0]*100 # this to force the fit to match FFF.
        return err # should not perform sum
    def response_dog_bulk(self, params):
        return (self.xstim * self.get_dog(*params)).sum(axis=1)
    def get_dog(self, amp1=10, sig1=10, amp2=5, sig2=30):
        gauss1 = amp1 * np.exp(self.nvfs/(TWOPI*sig1))
        gauss2 = amp2 * np.exp(self.nvfs/(TWOPI*sig2))
        return gauss1 - gauss2
    def fit_dog(self, initial_guess=None):
        # print 'try to fit dog parameter...'
        params_brute, _, _, _ = optimize.brute(
            self.ballpark_residuals_dog,
            initial_guess or self.ballpark_dog,
            Ns = 5,
            full_output = True,
        )
        params_lsq, _, _, _, _ = optimize.leastsq(
            self.lsq_residuals_dog,
            params_brute,
            ftol = 0.001,
            maxfev = 5000,#DXFV changed to 5000 from 1000
            full_output = True,
        )
        return DogParam(*params_lsq)
    @property
    def dog_param(self):
        if not self._dog_param:
            self._dog_param = self.fit_dog()
        return self._dog_param
    @property
    def dog_xy(self):
        return self.stretched.x, self.response_dog_bulk(self.dog_param)
    @property
    def dog_x(self):
        return self.stretched.x
    @property
    def dog_y(self):
        return self.response_dog_bulk(self.dog_param)
    def dog_function(self, sf, offset=0):
        return (self.stimulus(sf) * self.get_dog(*self.dog_param)).sum() - offset
    @property
    def preferred_sfreq(self):
        x, y = self.dog_xy
        pindex = y.argmax()
        # import ipdb; ipdb.set_trace()
        return Point(x[pindex], y[pindex])
    @property
    def peak_sfreq(self):
        pindex = self.ymeas.argmax()
        return Point(self.xfreq[pindex], self.ymeas[pindex])
    @property
    def y_for_bandwidth(self):
        return self.preferred_sfreq.y/2
    def solve_bandwidth(self):
        left, right = None, None
        x, y = self.dog_xy
        indice = np.abs(y - self.y_for_bandwidth).argsort()
        center_index = y.argmax()
        for index in indice:
            if index < center_index:
                left = index
                break
        for index in indice:
            if index > center_index:
                right = index
                break
        xleft = optimize.fsolve(self.dog_function, x[left], args=self.y_for_bandwidth, factor=0.1)[0]
        xright= optimize.fsolve(self.dog_function, x[right], args=self.y_for_bandwidth, factor=0.1)[0]
        return [
            (xleft, self.dog_function(xleft)),
            (xright, self.dog_function(xright))
        ]
    @property
    def bandwidth_ratio(self):
        try:
            left, right = self.solve_bandwidth()
            return np.sqrt(right[0] / left[0])
        except Exception as e:
            print 'exception in bandwidth_ratio:', type(e), str(e)
            return np.nan
    def make_cutoff(self, name, floor):
        _name = '_{}'.format(name)
        if not hasattr(self, _name):
            step_factor = 0.0001
            check_factor = 0.001
            guess = self.preferred_sfreq.x
            trial = 0
            secondpass = False
            while True:
                if trial > 10000:
                    if secondpass:
                        setattr(self, _name, None)
                        print 'failed on second pass'
                        break
                    else:
                        print 'trying second pass'
                        secondpass = True
                        trial = 0
                        check_factor = 0.01
                        continue
                trial += 1
                compare = self.dog_function(guess)
                diff = compare - floor
                if np.abs(diff) <= check_factor:
                    print 'found answer', diff, name, floor
                    setattr(self, _name, Point(guess, floor))
                    break
                else:
                    guess = guess + step_factor
        return getattr(self, _name)

    @property
    def dog_xy_ext(self): # to cpd 1.0
        func = interpolate.interp1d(self.xfreq, self.ymeas, bounds_error=False)
        stretched = np.linspace(self.xfreq[0], 1.0, 100)
        x = Stretched(stretched, func(stretched)).x
        xstim = np.array(map(self.stimulus, x))
        y = (xstim * self.get_dog(*self.dog_param)).sum(axis=1)
        return x, y

    def toDict(self):
        dog_x_ext, dog_y_ext = self.dog_xy_ext
        pref = self.preferred_sfreq.x
        peak = self.peak_sfreq.x
        ratio = self.bandwidth_ratio
        dog_x = self.dog_x.tolist()
        dog_y = self.dog_y.tolist()
        blank = self.blank
        flicker = self.flicker
        sfx = util.nan_for_list(self.xfreq.tolist())
        sfy = util.nan_for_list(self.ymeas.tolist())
        param = self.dog_param._asdict()
        plot = self.plot_io()
        # rc10 = self._rel_cutoff10
        # rc20 = self._rel_cutoff20
        rc33 = self._rel_cutoff33
        # c15 = self._cutoff15
        # c20 = self._cutoff20
        return util.nan_for_json(dict(
            pref = pref,
            peak = peak,
            ratio = ratio,
            dog_x = dog_x,
            dog_y = dog_y,
            dog_x_ext = dog_x_ext.tolist(),
            dog_y_ext = dog_y_ext.tolist(),
            blank = blank,
            flicker = flicker,
            sfx = sfx,
            sfy = sfy,
            param = param,
            plot = plot,
            # rc10 = rc10,
            # rc20 = rc20,
            rc33 = rc33,
            # c15 = c15,
            # c20 = c20
        ))
    def _plot(self):
        print 'Prepare plotting...'
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('SF Tuning Curve')
        ax.plot(self.xfreq, self.ymeas, label='original')
        x, y = self.dog_xy_ext
        ax.plot(x, y, label='fit')
        px, py = self.preferred_sfreq
        ax.plot(px, py, 'o', label='pref-sf')
        px, py = self.peak_sfreq
        ax.plot(px, py, 'o', label='peak-sf')


        pSF = self.preferred_sfreq.y
        # rel_cutoff10 = 0.1 * (pSF - self.flicker)
        # rel_cutoff20 = 0.2 * (pSF - self.flicker)
        rel_cutoff33 = 0.33 * (pSF - self.flicker)
        # cutoff15 = 0.15 # * pSF
        # cutoff20 = 0.2 # * pSF

        # rel_cutoff10 = self.make_cutoff('rel_cutoff10', rel_cutoff10)
        # rel_cutoff20 = self.make_cutoff('rel_cutoff20', rel_cutoff20)
        rel_cutoff33 = self.make_cutoff('rel_cutoff33', rel_cutoff33)
        # cutoff15 = self.make_cutoff('cutoff15', cutoff15)
        # cutoff20 = self.make_cutoff('cutoff20', cutoff20)

        # if rel_cutoff10:
        #     x, y = rel_cutoff10
        #     ax.scatter(x, y, label='SF Rel Cutoff 10', color='black', marker='x')
        # if rel_cutoff20:
        #     x, y = rel_cutoff20
        #     ax.scatter(x, y, label='SF Rel Cutoff 20', color='black', marker='*')
        if rel_cutoff33:
            x, y = rel_cutoff33
            ax.scatter(x, y, label='SF Rel Cutoff 33', color='black', marker='x')
        # if cutoff15:
        #     x, y = cutoff15
        #     ax.scatter(x, y, label='SF Cutoff 15', color='black', marker='v')
        # if cutoff20:
        #     x, y = cutoff20
        #     ax.scatter(x, y, label='SF Cutoff 20', color='black', marker='^')


        if not np.isnan(self.bandwidth_ratio):
            howmany = len(self.stretched.x)
            ax.plot(self.stretched.x, [self.preferred_sfreq.y]*howmany, linewidth=0.25, color='grey')
            ax.plot(self.stretched.x, [self.preferred_sfreq.y/2]*howmany, linewidth=0.25, color='grey')
            band_left, band_right = self.solve_bandwidth()
            ax.plot(*band_left, marker='o') #, label='l')
            ax.plot(*band_right, marker='o') #,  label='r')
        else:
            print 'unable to plot bandwidth'

        ax.legend()
        return plt, fig

    def plot_local(self, filename='fig.pdf'):
        print 'prepare local plot'
        plt, fig = self._plot()
        fig.savefig(filename, bbox_inches='tight')
        fig.clf()
        plt.close(fig)

    def plot_io(self, b64encode=True):
        plt, fig = self._plot()
        io = StringIO()
        if b64encode:
            fig.savefig(io, format='png', bbox_inches='tight')
            data = base64.b64encode(io.getvalue())
        else:
            fig.savefig(io, format='svg', bbox_inches='tight')
            data = io.getvalue()
        fig.clf()
        plt.close(fig)
        return data

    def plot(self):
        return self.plot_io(b64encode=False)
        # io = StringIO()
        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # ax.set_title('SF Tuning Curve')
        # ax.plot(self.xfreq, self.ymeas, label='measure', marker='o')
        # ax.plot(self.dog_x, self.dog_y, label='fit', color='red')
        # ax.legend()
        # fig.savefig(io, format='svg', bbox_inches='tight')
        # fig.clf()
        # plt.close(fig)
        # return io.getvalue()

#     def plot_psf(self): # preferred spatial frequency
#         px, py = self.preferred_sfreq
#         plot(px, py, 'o', label='pref-sf')
#         legend()
#     def plot_Psf(self): # peak spatial frequency
#         px, py = self.peak_sfreq
#         plot(px, py, 'o', label='peak-sf')
#         legend()
#     def plot_dog(self):
#         x, y = self.dog_xy
#         plot(x, y, label='fit')
#         legend()
#     def plot_floor(self):
#         if self.floor_xy:
#             x, y = self.floor_xy
#             scatter(x, y, label='floor', color='black')
#             legend()
#     def plot_original(self):
#         plot(self.xfreq, self.ymeas, label='original')
#         legend()
#     def plot_all(self):
#         self.plot_original()
#         self.plot_dog()
#         self.plot_psf()
#         self.plot_Psf()
#         self.plot_floor()
#         howmany = len(self.stretched.x)
#         plot(self.stretched.x, [self.preferred_sfreq.y]*howmany, linewidth=0.25, color='grey')
#         plot(self.stretched.x, [self.preferred_sfreq.y/2]*howmany, linewidth=0.25, color='grey')
#         band_left, band_right = self.solve_bandwidth()
#         plot(*band_left, marker='o', label='l')
#         plot(*band_right, marker='o',  label='r')
#         legend()

# from matplotlib.pyplot import *
