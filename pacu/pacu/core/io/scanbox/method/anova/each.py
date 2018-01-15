__package__ = '' # unicode package name error

import numpy as np
from scipy import stats
import random

from pacu.core.io.scanimage import util

def main(workspace, condition, roi, datatag, dff0s=None):
    n_panes = condition.info.get('focal_pane_args', {}).get('n', 1)
    pane_offset = workspace.cur_pane or 0
    if not dff0s:
        dff0s = roi.dttrialdff0s
    if datatag.trial_tf:
        oris = dff0s.filter_by(
            trial_sf=datatag.trial_sf,
            trial_contrast=datatag.trial_contrast,
            trial_tf=datatag.trial_tf # added by JZ
        )
    else:
        oris = dff0s.filter_by(
            trial_sf=datatag.trial_sf,
            trial_contrast=datatag.trial_contrast,
        )

    oris = [
        [np.nanmean(np.array(rep.value['on'][pane_offset::n_panes]))
        for rep in oris.filter_by(trial_ori=ori)]
    for ori in condition.orientations]
    bls = dff0s.filter_by(trial_blank=True)
    fls = dff0s.filter_by(trial_flicker=True)

    # If blank/flicker conditions are absent, off periods from random
    # set of trials is used (JZ)
    reps = condition.repetition
    num_trials = len(dff0s)

    if not bls:
        blank_trial_indices = random.sample(xrange(0, num_trials), reps)
        bls = [dff0s[i] for i in blank_trial_indices]
        blank = [np.nanmean(np.array(b.value['baseline'][pane_offset::n_panes])) for b in bls]
    else:
        blank = [np.nanmean(np.array(b.value['on'][pane_offset::n_panes])) for b in bls]

    if not fls:
        flicker_trial_indices = random.sample(xrange(0, num_trials), reps)
        fls = [dff0s[i] for i in flicker_trial_indices]
        flicker = [np.nanmean(np.array(f.value['baseline'][pane_offset::n_panes])) for f in fls]
    else:
        flicker = [np.nanmean(np.array(f.value['on'][pane_offset::n_panes])) for f in fls]

    try:
        flicker_non_nans = list(filter(np.isfinite, flicker))
        blank_non_nans = list(filter(np.isfinite, blank))
        oris_non_nans = [list(filter(np.isfinite, trial)) for trial in oris]
        return stats.f_oneway(blank_non_nans, flicker_non_nans, *oris_non_nans)
    except Exception as e:
        print 'Error on making Anova Each', str(e)
        return None, None

if __name__ == '__sbx_main__':
    f, p = main(workspace, condition, roi, datatag)
    datatag.f = 'nan' if np.isnan(f) else f
    datatag.p = 'nan' if np.isnan(p) else p
    print datatag.f, datatag.p, datatag.trial_sf, datatag.trial_contrast, datatag.trial_tf

if __name__ == '__sbx_stitch__':
    f, p = main(workspace, condition, roi, datatag, dff0s)
    datatag.f = 'nan' if np.isnan(f) else f
    datatag.p = 'nan' if np.isnan(p) else p
    print datatag.f, datatag.p, datatag.trial_sf, datatag.trial_contrast, datatag.trial_tf

