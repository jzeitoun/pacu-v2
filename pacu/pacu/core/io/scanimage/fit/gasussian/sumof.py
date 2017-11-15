###########################################################################
# Will deprecate below code by June 2016
#
import numpy as np
from scipy import optimize
from scipy.optimize import brute
from scipy.optimize import leastsq
from scipy.interpolate import interp1d

def get(x,p):
    global prefs
    A_1, A_2, sigma, offset=p
    if sigma>0:
        sumofgaussians= A_1*np.exp(-((x-prefs[0])/sigma)**2)+\
                        A_1*np.exp(-((x-prefs[1])/sigma)**2)+\
                        A_2*np.exp(-((x-prefs[2])/sigma)**2)+\
                        A_2*np.exp(-((x-prefs[3])/sigma)**2)+\
                        offset
    else:
        sumofgaussians=np.ones(x.shape)*offset

    return sumofgaussians

def get_residuals_brute(p,y_meas_stretch,x_stretch):
    err = y_meas_stretch-get(x_stretch,p)
    err=sum(err**2)
    return err

def curve_fit_brute(y_meas_stretch,x_fit):
    ranges=((0,1),(0,1),(15,60),((0,.01)))
    p_fit,residual,grid,Jout=brute(get_residuals_brute, ranges, args=(y_meas_stretch,x_fit),Ns=5,full_output=True,finish=None)
    return p_fit

def within_bounds(p):
    A_1, A_2, sigma, offset=p
    if A_1<0 or A_2<0:
        return False
    elif sigma>90 or sigma<15: # sigma>15 constraint in Chen et. al. 2013, about GCaMP6
        return False
    elif offset<0:
        return False
    else:
        return True

def get_residuals_leastsq(p,y,x):
    if not within_bounds(p):
        return 1e12
    err = y-get(x,p)
    return err

def stretch(x,y):
    x=np.append(x,360)
    y=np.append(y,y[0])
    f=interp1d(x,y,bounds_error=False)
    x_new=np.arange(0,360,1)
    return x_new, f(x_new)

def curve_fit_leastsq(p,y_meas_stretch,x_fit):
    leastsq_ans=leastsq(get_residuals_leastsq,p,args=(y_meas_stretch,x_fit), ftol=.001, maxfev=100, full_output=True, diag=(1,1,100,1) )
    p_fit=leastsq_ans[0]
    return p_fit

def get_preferred_orientation(x,y):
    # Niell and Stryker 2008
    x_rad=np.deg2rad(x)
    numerator=sum(y*np.exp(2j*x_rad))
    denomenator=sum(y)
    oPref=np.angle(numerator/denomenator,deg=True)
    if oPref<0:
        oPref+=360
    oPref=oPref/2
    return oPref

def fit(x, y_meas):
    global prefs
    x=np.array(x)
    y_meas=np.array(y_meas)
    oPref=get_preferred_orientation(x,y_meas) # it will always fall between 0 and 180
    oOppos=oPref+180
    oPref2=oPref+360
    oOppos2=oPref-180
    prefs=[oPref,oPref2,oOppos,oOppos2]
    x_fit, y_meas_stretch=stretch(x,y_meas)#DXFV - change to np.absolute(stretch(x,y_meas)) when trace flipped sign

    p_fit = curve_fit_brute(y_meas_stretch,x_fit)
    p_fit = curve_fit_leastsq(p_fit,y_meas_stretch,x_fit)

    if p_fit[0]>p_fit[1]:
        o1=oPref
        o2=oOppos
    else:
        o2=oPref
        o1=oOppos
    oPref=o1
    oOppos=o2

    y_fit=get(x_fit,p_fit)
    residuals=get_residuals_leastsq(p_fit,y_meas_stretch,x_fit)
    residual=sum(residuals**2)
    return (p_fit, residual, [x_fit, y_fit],[oPref, oOppos], y_meas_stretch)
#
# Will deprecate above code by June 2016
###########################################################################

from pacu.util.prop.memoized import memoized_property
from collections import namedtuple

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
        self.initial_guess = initial_guess or ((0, 1), (0, 1), (15, 60), (0, 0.01))
        self.global_o_pref = global_o_pref
        # if global_o_pref:
        #     print '\n====================================='
        #     print 'global o_pref', global_o_pref
        #     print 'o_prefs', self.o_prefs
        #     print '=====================================\n'
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
        numerator = np.nansum(self.ymeas*np.exp(2j*x_rad))
        o_pref = np.angle(numerator/np.nansum(self.ymeas), deg=True)
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
        return Fit(interp1d(x, y, bounds_error=False)(x_new), x_new) # y comes first
    @memoized_property
    def brute_fit(self):
        def get_residuals(params, y_meas_stretch, x_stretch):
            err = y_meas_stretch - self.function(x_stretch, params)
            return np.nansum(err**2)
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
            return 1e12
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
