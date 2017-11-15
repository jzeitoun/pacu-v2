import sys

import numpy as np
import scikits.bootstrap as bootstrap

from pacu.core.io.scanimage import util
from pacu.core.io.scanbox.method.fit.sogfit import SumOfGaussianFit
from pacu.core.io.scanbox.method.fit.dogfit import SpatialFrequencyDogFit

class BootFit(object):
    def __init__(self):
        self.rvs = []
    def stat_for_all(self, data):
        rmaxes = []
        for d in np.split(data, len(self.sfs), axis=1):
            vals = d['val']
            x_oris = d['ori'][0, :]
            y_meas = vals.mean(0)
            fit = SumOfGaussianFit(x_oris, y_meas)
            rmaxes.append(fit.r_max)
        fit = SpatialFrequencyDogFit(zip(self.sfs, rmaxes), self.flicker, self.blank)
        preferred_sf = fit.preferred_sfreq.x
        self.rvs.append(preferred_sf)
        print '.',
        return preferred_sf

class Bootstrap(object):
    mean = None
    std = None
    interval = None
    def toDict(self):
        return util.nan_for_json(dict(
            mean=self.mean,
            std=self.std
        ))
    n_samples = 500
    def __init__(self, bound_response, flicker, blank, sfs):
        self.bound_response = bound_response
        self.flicker = flicker
        self.blank = blank
        self.sfs = sfs
    def run(self):
        bf = BootFit()
        bf.sfs = self.sfs
        bf.flicker = self.flicker
        bf.blank = self.blank
        msg = ('Performing {} samples... ').format(self.n_samples)
        print msg
        try:
            self.interval = bootstrap.ci(
                data = self.bound_response,
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
        print 'INTERVAL:{s.interval}, MEAN: {s.mean}, STD: {s.std}'.format(s=self)
        # print stats
        print '{} unique preferred SF were made.'.format(len(set(stats)))
        return self




