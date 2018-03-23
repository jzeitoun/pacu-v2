__package__ = '' # unicode package name error

import numpy as np
import random

from pacu.core.io.scanbox.method.fit.dogfit import SpatialFrequencyDogFit
# did you sort datatag?
def tf_stats(workspace, condition, roi, trial_contrast, trial_sf, dff0s=None, fits=None):
    n_panes = condition.info.get('focal_pane_args', {}).get('n', 1)
    pane_offset = workspace.cur_pane or 0
    if not dff0s:
        dff0s = roi.dttrialdff0s
    if not fits:
        fits = roi.dtorientationsfits
    # Get trials belonging to current spatial frequency and contrast
    dts = fits.filter_by(trial_contrast=trial_contrast, trial_sf=trial_sf)
    bls = dff0s.filter_by(trial_blank=True)
    fls = dff0s.filter_by(trial_flicker=True)
    tf_rmax_set = [(dt.trial_tf, dt.value['r_max']) for dt in dts]

    # If blank/flicker conditions are absent, off periods from random
    # set of trials is used (JZ)
    reps = condition.repetition
    num_trials = len(dff0s)

    if not bls:
        blank_trial_indices = random.sample(xrange(0, num_trials), reps)
        bls = [dff0s[i] for i in blank_trial_indices]
        blank = np.nanmean(np.array([[bl.value['baseline'][pane_offset::n_panes]] for bl in bls]), axis=0).mean()
    else:
        blank = np.nanmean(np.array([[bl.value['on'][pane_offset::n_panes]] for bl in bls]), axis=0).mean()

    if not fls:
        flicker_trial_indices = random.sample(xrange(0, num_trials), reps)
        fls = [dff0s[i] for i in flicker_trial_indices]
        flicker = np.nanmean(np.array([[fl.value['baseline'][pane_offset::n_panes]] for fl in fls]), axis=0).mean()
    else:
        flicker = np.nanmean(np.array([[fl.value['on'][pane_offset::n_panes]] for fl in fls]), axis=0).mean()

    fit = SpatialFrequencyDogFit(tf_rmax_set, flicker, blank)

    return fit.toDict()

