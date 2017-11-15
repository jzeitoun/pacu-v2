from __future__ import division

class BaseTrace(object):
    start = 0
    end = -1
    def compensate(self, baseline, n_frames):
        """
        Dario mentioned 2016-09-19 UTC+9:
        Maybe default it to use all frames for meantrace and 1/4 of the baseline.
        """
        # early_index = len(baseline.array) - n_frames
        early_index = int(len(baseline.array) / 4)
        f_0 = baseline.array[early_index:].mean()
        if f_0 != 0:
            self.array[:] = (self.array - f_0)/f_0
            baseline.array[:] = (baseline.array - f_0)/f_0
