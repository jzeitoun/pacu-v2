__package__ = '' # unicode package name error

import numpy as np

from pacu.core.io.scanbox.method.fit.dogfit import SpatialFrequencyDogFit
# did you sort datatag?
def main(workspace, condition, roi, datatag):
    dts = roi.datatags.filter_by(method='sumof')
    bls = roi.datatags.filter_by(method='dff0', trial_blank=True)
    fls = roi.datatags.filter_by(method='dff0', trial_flicker=True)
    sf_rmax_set = [(dt.trial_sf, dt.value['r_max']) for dt in dts]
    blank = np.array([[bl.value['on']] for bl in bls]).mean(0).mean()
    flicker = np.array([[fl.value['on']] for fl in bls]).mean(0).mean()
    fit = SpatialFrequencyDogFit(sf_rmax_set, flicker, blank)
    return fit.toDict()

if __name__ == '__sbx_main__':
    datatag.value = main(workspace, condition, roi, datatag)
# cutoff repvalue on [capture frq
