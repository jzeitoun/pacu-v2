import numpy as np
from scipy import stats

from pacu.core.io.scanimage.response.base import BaseResponse
from pacu.core.io.scanimage import util

class ROIResponse(BaseResponse):
    cv = None
    @property
    def stats(self):
        if not self.normalfit:
            return {}
        g = self.normalfit.gaussian
        return util.nan_for_json(dict(
            tau = self.decay.tau,
            # bootstrap = self.bootstrap,
            osi = g.osi,
            dsi = g.dsi,
            sigma = g.sigma,
            o_pref = g.o_pref,
            r_max = g.r_max,
            residual = g.residual,
            anova = self.anova,
            ttest = self.ttest,
            cv = self.cv))
    @property
    def cv(self):
        angles = self.orientations.names
        sqrt, sin, cos, sum = np.sqrt, np.sin, np.cos, np.sum
        two_thetas = 2*(np.array(angles)/360)*2*np.pi
        r_thetas = self.normalfit.measure
        return sqrt(
            sum((r_thetas * sin(two_thetas)))**2 +
            sum((r_thetas * cos(two_thetas)))**2
        ) / sum(r_thetas)
    @property
    def anova(self):
        try:
            oris = self.orientations.windowed_ontimes
            if self.flicker and self.blank:
                b_reps = self.blank.windowed_mean_for_ontimes
                f_reps = self.flicker.windowed_mean_for_ontimes
                f, p = stats.f_oneway(b_reps, f_reps, *oris)
                return dict(f=f, p=p)
            elif self.flicker:
                f_reps = self.flicker.windowed_mean_for_ontimes
                f, p = stats.f_oneway(f_reps, *oris)
                return dict(f=f, p=p)
            elif self.blank:
                b_reps = self.blank.windowed_mean_for_ontimes
                f, p = stats.f_oneway(b_reps, *oris)
                return dict(f=f, p=p)
        except Exception as e:
            print 'anova each exception: ', e
            return {}
    @property
    def ttest(self):
        try:
            oris = self.orientations.windowed_ontimes
            names = self.orientations.names

            if self.flicker and self.blank:
                b_reps = self.blank.windowed_mean_for_ontimes
                f_reps = self.flicker.windowed_mean_for_ontimes
                values = [
                        dict(name=name, pvalue=stats.ttest_ind(b_reps, ori)[1])
                    for name, ori in zip(names, oris)
                ]
                values.insert(0,
                    dict(name='flicker', pvalue=stats.ttest_ind(b_reps, f_reps)[1])
                )
                return values
        except Exception as e:
            print e
            return []
#     @classmethod
#     def from_adaptor(cls, roi, trace, adaptor):
#         self = super(ROIResponse, cls).from_adaptor(roi, trace, adaptor)
#         return self
