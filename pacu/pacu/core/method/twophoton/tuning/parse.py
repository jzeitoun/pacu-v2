# -*- coding: utf-8 -*-

from __future__ import division # Enable the new behaviour
import numpy as np
import functools
# from ext.console import debug
from pacu.core.method.twophoton.gaussians.sum import fit, get_sumofgaussians
# import scikits.bootstrap as bootstrap
import cPickle

# I was going to use polysmooth for calculating f_0 but decided not to.
def polysmooth(v,polyorder):
    x=np.arange(len(v))
    z=np.polyfit(x,v,polyorder)
    p=np.poly1d(z)
    newV=p(x)
    return newV

def getCV(meanresponses, angles):
    sqrt, sin, cos, sum = np.sqrt, np.sin, np.cos, np.sum
    two_thetas = 2*(np.array(angles)/360)*2*np.pi
    R_thetas = meanresponses

    return sqrt(
        sum((R_thetas * sin(two_thetas)))**2 + sum((R_thetas * cos(two_thetas)))**2
    ) / sum(R_thetas)

def getOSI(meanresponses_p, o_peaks):
    '''returns the Orientation Selectivity Index (Niell and Stryker, 2008)'''
    A_1, A_2, sigma, offset=meanresponses_p
    theta_pref,theta_oppos = o_peaks
    theta_ortho=(theta_pref+theta_oppos)/2
    x=np.array([theta_pref,theta_ortho])
    R_pref,R_ortho=get_sumofgaussians(x, meanresponses_p)
    if R_pref+R_ortho<=0:
        return np.nan
    OSI=(R_pref-R_ortho)/(R_pref+R_ortho)
    return OSI

def getDSI(meanresponses_p, o_peaks):
    '''returns the Direction Selectivity Index (Niell and Stryker, 2008)'''
    A_1, A_2, sigma, offset=meanresponses_p
    theta_pref,theta_oppos = o_peaks
    x=np.array([theta_pref,theta_oppos])
    R_pref,R_opposite=get_sumofgaussians(x,meanresponses_p)
    if R_pref+R_opposite<=0:
        return np.nan
    DSI=(R_pref-R_opposite)/(R_pref+R_opposite)
    return DSI

# SPG 072414 added to extract tuning width
def getSigma(meanresponses_p):
    A_1, A_2, sigma, offset=meanresponses_p
    return sigma

# SPG 072414 added to extract preferred orientation
def getOpref(o_peaks):
    Opref, Ooppos=o_peaks
    return Opref

# SPG 072414 added to extract preferred maximum Response
def getRmax(meanresponses_fit):
    x_fit, y_fit=meanresponses_fit
    Rmax = max(y_fit)
    return Rmax

# def boot_fit(orientations, returns, data): # returns OSI
#     y_meas = data.mean(1)
#     meanresponses_p, _, _, o_peaks = fit(orientations, y_meas)
#     osi = getOSI(meanresponses_p, o_peaks)
#     returns.append(osi)
#     print '.',
#     return osi

def boot_fit(returns, data):
    vals = data['val']
    oris = data['ori'][0, :]
    y_meas = vals.mean(0)
    meanresponses_p, _, _, o_peaks = fit(oris, y_meas)
    osi = getOSI(meanresponses_p, o_peaks)
    returns.append(osi)
    print '.',
    return osi

# DXFV 2014.07.25 added to extract residual
#def getResidual(residual):
#    y_fit=get_sumofgaussians(x_fit,p_fit)
#    residuals=get_residuals_leastsq(p_fit,y_meas_stretch,x_fit)
#    residual=sum(residuals**2)
#    return residual

# Response -> Orientation -> Repetition
class Repetition():
    def __init__(self,repIDX,trace,c): #if repIDX is n, this is the n+1th stimulus played
        wait_interval = round(c['waitinterval_F'])
        self.repIDX=repIDX
        self.firstFrame=round(c['ontimes_F'][repIDX])
        self.lastFrame=self.firstFrame+round(c['duration_F'])
        self.baseline_firstFrame=self.firstFrame-wait_interval
        if self.baseline_firstFrame<0:
            print("Error: The first pre-stimulus blank isn't long enough.  This affects analysis.")
            self.baseline_firstFrame=0
        self.baseline_lastFrame=self.firstFrame-1

        self.trace=trace[self.firstFrame:self.lastFrame].copy()
        self.baseline_trace=trace[self.baseline_firstFrame:self.baseline_lastFrame].copy()

        # off-time traces HTK Oct 16 2015

        self.offtime_firstFrame = self.lastFrame
        if repIDX + 1 != len(c['sequence']): # if this rep is not occurred at very last
            self.offtime_firstFrame += 1
        self.offtime_lastFrame = self.offtime_firstFrame + wait_interval
        self.offtime_trace=trace[self.offtime_firstFrame:self.offtime_lastFrame].copy()

        #normalize using the last two seconds of the baseline trace as f_0
        f_0 = self.baseline_trace[
            len(self.baseline_trace) - int(0.5*c['captureFrequency']):
        ].mean()

        #DXFV 2014.07.25 playing with normalization parameters
        #DXFV 2014.11.11 changed segement of off stimulus to normalize to 1 because amblceilingfaan - this has been cloned on github.  This is no longer the current versionyope recordings are 3 seconds on 3 seconds off
        #HT 2015.01.06 commented below line to go back to the original code.
        #f_0=self.baseline_trace[len(self.baseline_trace)-int(3*c['captureFrequency']):].mean() # ceilingfaan - this has been cloned on github.  This is no longer the current version
        if f_0!=0:
            self.just_trace = self.trace
            self.just_baseline_trace = self.baseline_trace
            self.trace=(self.trace-f_0)/f_0
            self.baseline_trace=(self.baseline_trace-f_0)/f_0

class Orientation():
    ##########################################################
    # Modified by Hyungtae Kim <hyungtk@uci.edu>, in Nov 2014
    # In order for `ResponseFig` to display specific spatial frequency,
    # I made __init__ accepts `ori` so that it can free a tight coupling
    # with `conditionN`.
    #
    def __init__(self, conditionN, ori, trace, c):
        ''' condition number is the index of the orientation in c['orientations'].
        '''
        self.name=ori
        self.reps=[]
        # print '\nINIT ORIENTATION for condition', conditionN
        # debug.enter()
        for i in np.where(np.array(c['sequence'])==conditionN+1)[0]: #i is the index of the desired condition in the sequence
            # print 'Reps appending for Orientation', self
            self.reps.append(Repetition(i,trace,c))
            # print i, 'index rep made...check length'
        self.meantrace=np.array([a.trace for a in self.reps]).mean(0)
        try:
            self.meanbaseline_trace = np.array(
                [rep.baseline_trace for rep in self.reps]
            ).mean(0)
        except:
            pass

class Response(object):
    ##########################################################
    # Modified by Hyungtae Kim <hyungtk@uci.edu>, in Nov 2014
    # In order for `ResponseFig` to display specific spatial frequency,
    # I splited an initialization part into a set of new functions.
    # And make __init__ accepts optional sfreq_meta so that it can call `self.make`
    # with a specific spatial frequency of interest.
    #
    cond = None
    meta = None
    matrix = ()
    @classmethod
    def rmax_by_sfreq(cls, trace, cond, freq_meta):
        FreqMeta = type(freq_meta)
        n_tf = len(freq_meta.tfrequencies)
        return [
            (
                sfreq,
                max(
                    cls(trace, cond, FreqMeta(cond, sfindex, tfindex)).Rmax
                    for tfindex in range(n_tf)
                )
            ) for sfindex, sfreq in enumerate(freq_meta.sfrequencies)
        ]
    def __init__(self, trace, c, freq_meta=None):
        self.orientations = []
        self.append_orientations(trace, c, freq_meta)
        self.make_response(c, freq_meta)
        self.cond = c
        self.meta = freq_meta
    def append_orientations(self, trace, c, meta=None):
        zipped = (meta.conditions_and_orientations
            if meta else enumerate(c['orientations']))
        for i, ori in zipped:
            self.orientations.append(Orientation(i, ori, trace, c))
        ##########################################################
        # Modified by Hyungtae Kim <hyungtk@uci.edu>, in Apr 2015
        # This is for displaying blank and full field flicker.
        #
        if meta and meta.blank_index:
            self.blank = Orientation(meta.blank_index, 'blank', trace, c)
        if meta and meta.flicker_index:
            self.flicker = Orientation(meta.flicker_index, 'flicker', trace, c)
    blank = None
    flicker = None

    def make_response(self, c, meta=None):
        orientations = c['orientations']
        capture_freq = c['captureFrequency']
        # DXF changes the segment of the stimulation period used to calculate the response
        self.meanresponses = [o.meantrace.mean() for o in self.orientations]
        #original: self.meanresponses=[o.meantrace[1:int(3*c['captureFrequency'])].mean() for o in self.orientations]
        #DXFV - to change segment of stimulation period used to calculate from x to y seconds use "self.meanresponses=[o.meantrace[int(1*c['captureFrequency']):int(3*c['captureFrequency'])].mean() for o in self.orientations]"
        self.meanresponses = [
            o.meantrace[int(1*capture_freq):int(6*capture_freq)].mean()
            for o in self.orientations
        ]
        # assign 4 attributes
        self.meanresponses_p  ,\
        self.residual         ,\
        self.meanresponses_fit,\
        self.o_peaks           = fit(orientations, self.meanresponses)

        self.OSI = getOSI(self.meanresponses_p, self.o_peaks)
        self.DSI = getDSI(self.meanresponses_p, self.o_peaks)

        # SPG 072314 to do \: import the least squares fit from
        # sumofgaussians and pull out the values for Opref and sigma to
        # add to response so that it can be plotted in windows
        self.sigma = getSigma(self.meanresponses_p)
        self.Opref = getOpref(self.o_peaks)
        self.Rmax = getRmax(self.meanresponses_fit)

        # DXFV 2014.07.25 to display residuals as
        # part of the axis label in the fit plot
        self.Residual=self.residual

        self.CV = getCV(meanresponses=self.meanresponses, angles=c['orientations'])

        if meta:
            self.matrix = meta.make_export_data(self)
            self.max_orientation_index = np.argmax(self.meanresponses)
            self.max_orientation_value = meta.orientations[self.max_orientation_index]
            self.max_orientation = self.orientations[self.max_orientation_index]
        # debug.enter()

    def bootstrap_dump(self, filename):
        data = cPickle.dumps(self.bootstrap_data)
        with open(filename, 'wb') as f:
            f.write(data)

    @property
    def bootstrap_data(self):
        orientations = self.cond['orientations']
        capture_freq = self.cond['captureFrequency']
        resp = np.array([
            [
                rep.trace[int(1*capture_freq):int(6*capture_freq)].mean()
                for rep in o.reps
            ] for o in self.orientations
        ])
        return dict(ori=orientations, cfreq=capture_freq, resp=resp)

    def bootstrap_stat(self, n_samples=1000):
        bdata = self.bootstrap_data
        orientations = bdata.get('ori')
        capture_freq = bdata.get('cfreq')
        responses = bdata.get('resp')
        bound_dtype = [('val', float), ('ori', float)]
        bound = [
            [(value, ori) for value in values]
            for values, ori in zip(responses, orientations)]
        bound_response = np.array(bound, dtype=bound_dtype).T

        returns = []
        interval = bootstrap.ci(
            data = bound_response,
            statfunction = functools.partial(boot_fit, returns),
            n_samples = n_samples
        )

        stats = returns[:n_samples]
        nmean, nstd = np.nanmean(stats), np.nanstd(stats)
        print
        print 'INTERVAL:{}, MEAN: {}, STD: {}'.format(interval, nmean, nstd)
        return interval, nmean, nstd
    def mean_rep_traces_by_orientations(self):
        return [
            [rep.trace.mean() for rep in ori.reps]
            for ori in self.orientations
        ]
# 
# from __future__ import absolute_import
# from __future__ import division # Enable the new behaviour
# 
# import functools
# 
# import numpy as np
# # import scikits.bootstrap as bootstrap
# 
# from pacu.core.method.twophoton.gaussians.sum import fit, get_sumofgaussians
# # from ext.console import debug
# 
# # I was going to use polysmooth for calculating f_0 but decided not to.
# def polysmooth(v,polyorder):
#     x=np.arange(len(v))
#     z=np.polyfit(x,v,polyorder)
#     p=np.poly1d(z)
#     newV=p(x)
#     return newV
# 
# def getCV(meanresponses, angles):
#     sqrt, sin, cos, sum = np.sqrt, np.sin, np.cos, np.sum
#     two_thetas = 2*(np.array(angles)/360)*2*np.pi
#     R_thetas = meanresponses
# 
#     return sqrt(
#         sum((R_thetas * sin(two_thetas)))**2 + sum((R_thetas * cos(two_thetas)))**2
#     ) / sum(R_thetas)
# 
# def getOSI(meanresponses_p, o_peaks):
#     '''returns the Orientation Selectivity Index (Niell and Stryker, 2008)'''
#     A_1, A_2, sigma, offset=meanresponses_p
#     theta_pref,theta_oppos = o_peaks
#     theta_ortho=(theta_pref+theta_oppos)/2
#     x=np.array([theta_pref,theta_ortho])
#     R_pref,R_ortho=get_sumofgaussians(x, meanresponses_p)
#     if R_pref+R_ortho<=0:
#         return np.nan
#     OSI=(R_pref-R_ortho)/(R_pref+R_ortho)
#     return OSI
# 
# def getDSI(meanresponses_p, o_peaks):
#     '''returns the Direction Selectivity Index (Niell and Stryker, 2008)'''
#     A_1, A_2, sigma, offset=meanresponses_p
#     theta_pref,theta_oppos = o_peaks
#     x=np.array([theta_pref,theta_oppos])
#     R_pref,R_opposite=get_sumofgaussians(x,meanresponses_p)
#     if R_pref+R_opposite<=0:
#         return np.nan
#     DSI=(R_pref-R_opposite)/(R_pref+R_opposite)
#     return DSI
# 
# # SPG 072414 added to extract tuning width
# def getSigma(meanresponses_p):
#     A_1, A_2, sigma, offset=meanresponses_p
#     return sigma
# 
# # SPG 072414 added to extract preferred orientation
# def getOpref(o_peaks):
#     Opref, Ooppos=o_peaks
#     return Opref
# 
# # SPG 072414 added to extract preferred maximum Response
# def getRmax(meanresponses_fit):
#     x_fit, y_fit=meanresponses_fit
#     Rmax = max(y_fit)
#     return Rmax
# 
# def boot_fit(returns, data):
#     vals = data['val']
#     oris = data['ori'][0, :]
#     y_meas = vals.mean(0)
#     meanresponses_p, _, _, o_peaks = fit(oris, y_meas)
#     osi = getOSI(meanresponses_p, o_peaks)
#     returns.append(osi)
#     print '.',
#     return osi
# 
# # DXFV 2014.07.25 added to extract residual
# #def getResidual(residual):
# #    y_fit=get_sumofgaussians(x_fit,p_fit)
# #    residuals=get_residuals_leastsq(p_fit,y_meas_stretch,x_fit)
# #    residual=sum(residuals**2)
# #    return residual
# 
# # Response -> Orientation -> Repetition
# class Repetition():
#     def __init__(self,repIDX,trace,c): #if repIDX is n, this is the n+1th stimulus played
#         wait_interval = (round(c.waitinterval_F))
#         self.repIDX=repIDX
#         self.firstFrame = (round(c.ontimes_F[repIDX]))
#         self.lastFrame = self.firstFrame + (round(c.duration_F))
#         self.baseline_firstFrame = self.firstFrame - wait_interval
#         if self.baseline_firstFrame < 0:
#             print("Error: The first pre-stimulus blank isn't long enough.  This affects analysis.")
#             self.baseline_firstFrame = 0
#         self.baseline_lastFrame = self.firstFrame - 1
# 
#         self.trace=trace[self.firstFrame:self.lastFrame].copy()
#         self.baseline_trace=trace[self.baseline_firstFrame:self.baseline_lastFrame].copy()
# 
#         # off-time traces HTK Oct 16 2015
# 
#         self.offtime_firstFrame = self.lastFrame
#         if repIDX + 1 != len(c.sequence): # if this rep is not occurred at very last
#             self.offtime_firstFrame += 1
#         self.offtime_lastFrame = self.offtime_firstFrame + wait_interval
# 
#         self.offtime_trace=trace[self.offtime_firstFrame:self.offtime_lastFrame].copy()
# 
#         #normalize using the last two seconds of the baseline trace as f_0
#         f_0 = self.baseline_trace[
#             len(self.baseline_trace) - int(0.5*c.captureFrequency):
#         ].mean()
# 
#         #DXFV 2014.07.25 playing with normalization parameters
#         #DXFV 2014.11.11 changed segement of off stimulus to normalize to 1 because amblceilingfaan - this has been cloned on github.  This is no longer the current versionyope recordings are 3 seconds on 3 seconds off
#         #HT 2015.01.06 commented below line to go back to the original code.
#         #f_0=self.baseline_trace[len(self.baseline_trace)-int(3*c['captureFrequency']):].mean() # ceilingfaan - this has been cloned on github.  This is no longer the current version
#         if f_0!=0:
#             self.just_trace = self.trace
#             self.just_baseline_trace = self.baseline_trace
#             self.trace=(self.trace-f_0)/f_0
#             self.baseline_trace=(self.baseline_trace-f_0)/f_0
# 
# class Orientation():
#     ##########################################################
#     # Modified by Hyungtae Kim <hyungtk@uci.edu>, in Nov 2014
#     # In order for `ResponseFig` to display specific spatial frequency,
#     # I made __init__ accepts `ori` so that it can free a tight coupling
#     # with `conditionN`.
#     #
#     def __init__(self, conditionN, ori, trace, c):
#         ''' condition number is the index of the orientation in c['orientations'].
#         '''
#         self.name=ori
#         self.reps=[]
#         # print '\nINIT ORIENTATION for condition', conditionN
#         # debug.enter()
#         for i in np.where(np.array(c.sequence)==conditionN+1)[0]: #i is the index of the desired condition in the sequence
#             # print 'Reps appending for Orientation', self
#             self.reps.append(Repetition(i,trace,c))
#             # print i, 'index rep made...check length'
#         self.meantrace=np.array([a.trace for a in self.reps]).mean(0)
#         try:
#             self.meanbaseline_trace = np.array(
#                 [rep.baseline_trace for rep in self.reps]
#             ).mean(0)
#         except:
#             pass
# 
# class Response(object):
#     ##########################################################
#     # Modified by Hyungtae Kim <hyungtk@uci.edu>, in Nov 2014
#     # In order for `ResponseFig` to display specific spatial frequency,
#     # I splited an initialization part into a set of new functions.
#     # And make __init__ accepts optional sfreq_meta so that it can call `self.make`
#     # with a specific spatial frequency of interest.
#     #
#     cond = None
#     meta = None
#     matrix = ()
#     @classmethod
#     def rmax_by_sfreq(cls, trace, cond, freq_meta):
#         FreqMeta = type(freq_meta)
#         n_tf = len(freq_meta.tfrequencies)
#         return [
#             (
#                 sfreq,
#                 max(
#                     cls(trace, cond, FreqMeta(cond, sfindex, tfindex)).Rmax
#                     for tfindex in range(n_tf)
#                 )
#             ) for sfindex, sfreq in enumerate(freq_meta.sfrequencies)
#         ]
#     def __init__(self, trace, c, freq_meta=None):
#         self.orientations = []
#         self.append_orientations(np.array(trace), c, freq_meta)
#         self.make_response(c, freq_meta)
#         self.cond = c
#         self.meta = freq_meta
#     def append_orientations(self, trace, c, meta=None):
#         zipped = (meta.conditions_and_orientations
#             if meta else enumerate(c.orientations))
#         for i, ori in zipped:
#             self.orientations.append(Orientation(i, ori, trace, c))
#         ##########################################################
#         # Modified by Hyungtae Kim <hyungtk@uci.edu>, in Apr 2015
#         # This is for displaying blank and full field flicker.
#         #
#         if meta and meta.blank_index:
#             self.blank = Orientation(meta.blank_index, 'blank', trace, c)
#         if meta and meta.flicker_index:
#             self.flicker = Orientation(meta.flicker_index, 'flicker', trace, c)
#     blank = None
#     flicker = None
# 
#     def make_response(self, c, meta=None):
#         orientations = c.orientations
#         capture_freq = c.captureFrequency
#         self.meanresponses = [o.meantrace.mean() for o in self.orientations]
#         self.meanresponses = [
#             o.meantrace[int(1*capture_freq):int(2*capture_freq)].mean()
#             for o in self.orientations
#         ]
#         # assign 4 attributes
#         self.meanresponses_p  ,\
#         self.residual         ,\
#         self.meanresponses_fit,\
#         self.o_peaks           = fit(orientations, self.meanresponses)
# 
#         self.OSI = getOSI(self.meanresponses_p, self.o_peaks)
#         self.DSI = getDSI(self.meanresponses_p, self.o_peaks)
# 
#         # SPG 072314 to do \: import the least squares fit from
#         # sumofgaussians and pull out the values for Opref and sigma to
#         # add to response so that it can be plotted in windows
#         self.sigma = getSigma(self.meanresponses_p)
#         self.Opref = getOpref(self.o_peaks)
#         self.Rmax = getRmax(self.meanresponses_fit)
# 
#         # DXFV 2014.07.25 to display residuals as
#         # part of the axis label in the fit plot
#         self.Residual=self.residual
# 
#         self.CV = getCV(meanresponses=self.meanresponses, angles=c.orientations)
# 
#         if meta:
#             self.matrix = meta.make_export_data(self)
#             self.max_orientation_index = np.argmax(self.meanresponses)
#             self.max_orientation_value = meta.orientations[self.max_orientation_index]
#             self.max_orientation = self.orientations[self.max_orientation_index]
# 
#     def bootstrap_dump(self, filename):
#         data = cPickle.dumps(self.bootstrap_data)
#         with open(filename, 'wb') as f:
#             f.write(data)
# 
#     @property
#     def bootstrap_data(self):
#         orientations = self.cond['orientations']
#         capture_freq = self.cond['captureFrequency']
#         resp = np.array([
#             [
#                 rep.trace[int(1*capture_freq):int(6*capture_freq)].mean()
#                 for rep in o.reps
#             ] for o in self.orientations
#         ])
#         return dict(ori=orientations, cfreq=capture_freq, resp=resp)
# 
#     def bootstrap_stat(self, n_samples=500):
#         bdata = self.bootstrap_data
#         orientations = bdata.get('ori')
#         capture_freq = bdata.get('cfreq')
#         responses = bdata.get('resp')
#         bound_dtype = [('val', float), ('ori', float)]
#         bound = [
#             [(value, ori) for value in values]
#             for values, ori in zip(responses, orientations)]
#         bound_response = np.array(bound, dtype=bound_dtype).T # note "T"
# 
#         returns = []
#         interval = bootstrap.ci(
#             data = bound_response,
#             statfunction = functools.partial(boot_fit, returns),
#             n_samples = n_samples
#         )
# 
#         stats = returns[:n_samples]
#         nmean, nstd = np.nanmean(stats), np.nanstd(stats)
#         print 'MEAN: {}, STD: {}'.format(nmean, nstd)
#         return interval, mean, std
