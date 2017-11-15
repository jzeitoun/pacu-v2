from __future__ import division
from __future__ import absolute_import

import sys

import numpy as np
import scikits.bootstrap as bootstrap

from pacu.util.prop.memoized import memoized_property
from pacu.core.io.scanimage.fit.gasussian.sumof import SumOfGaussianFit
from pacu.core.io.scanimage.fit.gasussian.sfreqdog import SpatialFrequencyDogFit
from pacu.core.io.scanimage import util

bound_dtype = [('val', float), ('ori', float)]

class BootFit(object):
    def __init__(self):
        self.rvs = []
    def stat(self, data):
        vals = data['val']
        x_oris = data['ori'][0, :]
        y_meas = vals.mean(0)
        fit = SumOfGaussianFit(x_oris, y_meas)
        osi = fit.osi
        self.rvs.append(osi)
        print '.',
        return osi
    def stat_for_all(self, data):
        rmaxes = []
        for d in np.split(data, len(self.sfs), axis=1):
            vals = d['val']
            x_oris = d['ori'][0, :]
            y_meas = vals.mean(0)
            fit = SumOfGaussianFit(x_oris, y_meas)
            rmaxes.append(fit.r_max)
        fit = SpatialFrequencyDogFit(zip(self.sfs, rmaxes), self.fff, self.blank)
        preferred_sf = fit.preferred_sfreq.x
        self.rvs.append(preferred_sf)
        print '.',
        # print 'RMax: ' + str(rmaxes)
        # print 'Pref SF: ' + str(preferred_sf)
        return preferred_sf

class BootstrapResponse(object):
    n_samples = 500
    mean = None
    std = None
    interval = None
    def toDict(self):
        return util.nan_for_json(dict(
            mean=self.mean,
            std=self.std
        ))
    def make_bound_data(self, response):
        oris = response.orientations.names
        resps = response.orientations.windowed_ontimes
        bound = [
            [(value, ori) for value in values]
            for values, ori in zip(resps, oris)]
        return np.array(bound, dtype=bound_dtype).T
    @classmethod
    def from_adaptor(cls, response, adaptor):
        self = cls()
        msg = ('Creating bootstrap response {} for {} samples. '
               'It may take few minutes.').format(response.sfreq, self.n_samples)
        print msg
        bound_response = self.make_bound_data(response)
        return self.run(bound_response)
    @classmethod
    def from_adaptor_for_sf(cls, responses, fff, blank):
        self = cls()
        bounds = np.concatenate([
            self.make_bound_data(resp) for sf, resp in responses], axis=1)
        sfs = [sf for sf, _ in responses]
        return self.run_for_all(bounds, sfs, fff, blank)
    def run(self, bound_response):
        bf = BootFit()
        try:
            self.interval = bootstrap.ci(
                data = bound_response,
                statfunction = bf.stat,
                n_samples = self.n_samples
            )
            stats = bf.rvs[:self.n_samples]
            self.mean, self.std = np.nanmean(stats), np.nanstd(stats)
        except Exception as e:
            sys.stderr.write(str(e))
            sys.stderr.flush()
        # print 'INTERVAL:{s.interval}, MEAN: {s.mean}, STD: {s.std}'.format(s=self)
        return self
    def run_for_all(self, bound_response, sfs, fff, blank, n_samples=500):
        bf = BootFit()
        bf.sfs = sfs
        bf.fff = fff.mean if fff else None
        bf.blank = blank.mean if blank else None
        self.n_samples = n_samples
        msg = ('Performing {} samples... ').format(self.n_samples)
        print msg
        try:
            self.interval = bootstrap.ci(
                data = bound_response,
                statfunction = bf.stat_for_all,
                n_samples = self.n_samples
            )
            stats = bf.rvs[:self.n_samples]
            self.mean, self.std = np.nanmean(stats), np.nanstd(stats)
        except Exception as e:
            stats = bf.rvs[:self.n_samples]
            self.mean, self.std = np.nanmean(stats), np.nanstd(stats)
            sys.stderr.write(str(e))
            sys.stderr.flush()
        # print 'INTERVAL:{s.interval}, MEAN: {s.mean}, STD: {s.std}'.format(s=self)
        # print stats
        print '{} unique preferred SF were made.'.format(len(set(stats)))
        return self
