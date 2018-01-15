__package__ = '' # unicode package name error

from collections import OrderedDict

import numpy as np
import random
from scipy import stats

from pacu.core.io.scanimage import util

def ori_by_sf(trials, sfs, oris):
    return OrderedDict([
        (
            sf,
            OrderedDict([
            (
                ori,
                trials.filter_by(trial_sf=sf, trial_ori=ori)
            )
            for ori in oris])
        ) for sf in sfs])

def main(workspace, condition, roi, datatag, dff0s=None):
    n_panes = condition.info.get('focal_pane_args', {}).get('n', 1)
    pane_offset = workspace.cur_pane or 0

    if not dff0s:
        dff0s = roi.dttrialdff0s

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

    if datatag.trial_tf:
        all_trials = dff0s.filter_by(
            trial_contrast=datatag.trial_contrast,
            trial_tf=datatag.trial_tf,
            trial_flicker=False,
            trial_blank=False)
    else:
        all_trials = dff0s.filter_by(
            trial_contrast=datatag.trial_contrast,
            trial_flicker=False,
            trial_blank=False)
    trials = ori_by_sf(all_trials, condition.sfrequencies, condition.orientations)

    # all_oris = [
    #     [np.nanmean(np.array(rep.value['on'][pane_offset::n_panes])) for rep in reps]
    #     for sf, oris in roi.dt_ori_by_sf(datatag.trial_contrast).items()
    #     for ori, reps in oris.items()
    # ]

    all_oris = [
        [np.nanmean(np.array(rep.value['on'][pane_offset::n_panes])) for rep in reps]
        for sf, oris in trials.items()
        for ori, reps in oris.items()
    ]

    matrix = np.array([blank, flicker] + all_oris).T
    flicker_non_nans = list(filter(np.isfinite, flicker))
    blank_non_nans = list(filter(np.isfinite, blank))
    all_oris_non_nans = [list(filter(np.isfinite, trial)) for trial in all_oris]
    f, p = stats.f_oneway(flicker_non_nans, blank_non_nans, *all_oris_non_nans)
    return util.nan_for_json(dict(f=f, p=p, matrix=matrix.tolist()))

if __name__ == '__sbx_main__':
    datatag.value = main(workspace, condition, roi, datatag)

if __name__ == '__sbx_stitch__':
    datatag.value = main(workspace, condition, roi, datatag, dff0s)
