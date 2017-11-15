from collections import namedtuple

import numpy as np
from scipy import optimize
from scipy.interpolate import interp1d

from pacu.util.prop.memoized import memoized_property

Fit = namedtuple('Fit', 'y x') # note order

class SumOfGaussianFit(object):
    def __init__(self,
            xoris,
            ymeas,
            global_o_pref=None,
            initial_guess=None,
        ):
        self.xoris = xoris
        self.ymeas = ymeas
        self.global_o_pref = global_o_pref
        self.initial_guess = initial_guess or ((0, 0.5), (0, 0.5), (15, 60), (0, 0.01))
        print 'SoG fit with params', self.initial_guess
    def function(self, x, params):
        A_1, A_2, sigma, offset = params
        return (
            A_1*np.exp(-((x - self.o_prefs[0])/sigma)**2) +
            A_1*np.exp(-((x - self.o_prefs[1])/sigma)**2) +
            A_2*np.exp(-((x - self.o_prefs[2])/sigma)**2) +
            A_2*np.exp(-((x - self.o_prefs[3])/sigma)**2) +
            offset) if sigma > 0 else np.ones(x.shape)*offset
    @memoized_property
    def preferred_orientation(self): # Niell and Stryker 2008
        if self.global_o_pref:
            # print 'using global OPref', self.global_o_pref
            return self.global_o_pref
        x_rad = np.deg2rad(self.xoris)
        numerator = sum(self.ymeas*np.exp(2j*x_rad))
        o_pref = np.angle(numerator/sum(self.ymeas), deg=True)
        if o_pref < 0:
            o_pref += 360
        half_phase = o_pref/2
        half_phase %= 360
        return half_phase
    @memoized_property
    def o_prefs(self):
        o_pref1 = self.preferred_orientation
        o_oppo1 = o_pref1 + 180
        o_pref2 = o_pref1 + 360
        o_oppo2 = o_pref1 - 180
        o_pref1 %= 360
        o_pref2 %= 360
        o_oppo1 %= 360
        o_oppo2 %= 360
        return o_pref1, o_pref2, o_oppo1, o_oppo2
    @memoized_property
    def stretched(self):
        x = np.append(self.xoris, 360)
        y = np.append(self.ymeas, self.ymeas[0])
        x_new = np.arange(0, 360, 1)
        #x_new = np.arange(np.min(x), np.max(x)) # modified by JZ because orientations might not span 0 - 360
        return Fit(interp1d(x, y)(x_new), x_new) # y comes first
    @memoized_property
    def brute_fit(self):
        def get_residuals(params, y_meas_stretch, x_stretch):
            err = y_meas_stretch - self.function(x_stretch, params)
            return sum(err**2)
        fit_params, _, _, _ = optimize.brute(
            get_residuals,
            self.initial_guess,
            args = self.stretched,
            Ns = 5, full_output = True, finish = None)
        return fit_params
    @memoized_property
    def leastsq_fit(self):
        fit_params, _, _, _, _ = optimize.leastsq(
            self.get_residuals_leastsq,
            self.brute_fit,
            args = self.stretched,
            ftol = 0.001,
            maxfev = 100,
            full_output = True,
            diag = (1, 1, 100, 1)
            # diag : sequence, optional
            # N positive entries that serve as a scale factors for the variables.
        )
        return fit_params
    @memoized_property
    def fit_params(self):
        return self.leastsq_fit
    @memoized_property
    def o_peaks(self):
        o_pref1, _, o_oppo1, _ = self.o_prefs
        p1, p2, _, _ = self.fit_params
        return (o_pref1, o_oppo1) if p1 > p2 else (o_oppo1, o_pref1)
    def within_bounds(self, params):
        A_1, A_2, sigma, offset = params
        if A_1 < 0 or A_2 < 0:
            return False
        # sigma > 15 constraint in Chen et. al. 2013, about GCaMP6
        elif sigma > 90 or sigma < 15:
            return False
        else:
            return not offset < 0
    def get_residuals_leastsq(self, params, y, x):
        if not self.within_bounds(params):
            print('WARNING: SIGMA IS OUTSIDE THE NORMAL BOUNDS')
            #return 1e12  # commented out to allow single orientation
        return y - self.function(x, params)
    @memoized_property
    def x_fit(self):
        return self.stretched.x
    @memoized_property
    def y_fit(self):
        return self.function(self.stretched.x, self.leastsq_fit)
    @memoized_property
    def residual(self):
        return sum(
            self.get_residuals_leastsq(self.leastsq_fit, *self.stretched)**2)
    @memoized_property
    def legacy_summary(self): # to conform with Ceiling Faan
        return (
            self.fit_params,
            self.residual,
            [self.stretched.x, self.y_fit],
            self.o_peaks,
            self.stretched.y
        )
    @property
    def osi(self):
        '''returns the Orientation Selectivity Index (Niell and Stryker, 2008)'''
        theta_pref, theta_oppos = self.o_peaks
        theta_ortho = (theta_pref + theta_oppos)/2
        x = np.array([theta_pref, theta_ortho])
        r_pref, r_ortho = self.function(x, self.fit_params)
        if r_pref + r_ortho <= 0:
            return np.nan
        return (r_pref - r_ortho)/(r_pref + r_ortho)
    @property
    def dsi(self):
        '''returns the Direction Selectivity Index (Niell and Stryker, 2008)'''
        theta_pref, theta_oppos = self.o_peaks
        x = np.array([theta_pref, theta_oppos])
        r_pref, r_opposite = self.function(x, self.fit_params)
        if r_pref + r_opposite <= 0:
            return np.nan
        return (r_pref - r_opposite)/(r_pref + r_opposite)
    @property
    def cv(self):
        sqrt, sin, cos, sum = np.sqrt, np.sin, np.cos, np.sum
        two_thetas = 2*(np.array(self.xoris)/360)*2*np.pi
        R_thetas = self.ymeas
        # R_thetas = R_thetas + np.abs(np.min(R_thetas)) # sets most negative mean response to zero
        return sqrt(
            sum((R_thetas * sin(two_thetas)))**2 + sum((R_thetas * cos(two_thetas)))**2
        ) / sum(R_thetas)
    # Added by (JZ)
    @property
    def dcv(self):
        sqrt, sin, cos, sum = np.sqrt, np.sin, np.cos, np.sum
        thetas = (np.array(self.xoris)/360)*2*np.pi
        R_thetas = self.ymeas
        # R_thetas = R_thetas + np.abs(np.min(R_thetas)) # sets most negative mean response to zero
        return sqrt(
            sum((R_thetas * sin(thetas)))**2 + sum((R_thetas * cos(thetas)))**2
        ) / sum(R_thetas)
    @property
    def sigma(self):
        return self.fit_params[2]
    @property
    def o_pref(self):
        return self.o_peaks[0]
    @property
    def r_max(self):
        return self.y_fit.max()
    @property
    def r_pref(self):
        return self.function(self.o_pref, self.fit_params)
    def response_at(self, orientation):
        return self.function(orientation, self.fit_params)
