__package__ = '' # unicode package name error

import numpy as np

from pacu.core.io.scanbox.method.fit.dogfit import SpatialFrequencyDogFit
# did you sort datatag?
def main(workspace, condition, roi, datatag):
    dts = roi.datatags.filter_by(method='sumof')
    bls = roi.datatags.filter_by(method='dff0', trial_blank=True)
    fls = roi.datatags.filter_by(method='dff0', trial_flicker=True)
    sf_rmax_set = [(dt.trial_sf, dt.value['r_max']) for dt in dts]

    # Adding for situations where blank/flicker was forgotten (JZ)
    reps = condition.repetition
    num_trials = len(dff0s)

    if not bls:
        blank_trial_indices = random.sample(xrange(0, num_trials), reps)
        bls = [dff0s[i] for i in random_trial_indices]
        blank = np.array([[bl.value['off']] for bl in bls]).mean(0).mean()
    else:
        blank = np.array([[bl.value['on']] for bl in bls]).mean(0).mean()

    if not fls:
        flicker_trial_indices = random.sample(xrange(0, num_trials), reps)
        fls = [dff0s[i] for i in random_trial_indices]
        flicker = np.array([[fl.value['off']] for fl in fls]).mean(0).mean()
    else:
        flicker = np.array([[fl.value['on']] for fl in fls]).mean(0).mean()

    fit = SpatialFrequencyDogFit(sf_rmax_set, flicker, blank)
    return fit.toDict()

if __name__ == '__sbx_main__':
    datatag.value = main(workspace, condition, roi, datatag)
# cutoff repvalue on [capture frq
