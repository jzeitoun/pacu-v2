__package__ = '' # unicode package name error

import numpy as np
import random

from pacu.core.io.scanbox.method.fit.sogfit import SumOfGaussianFit

def tf_bestpref(workspace, condition, roi, trial_contrast, trial_sf, dff0s=None):
    if not dff0s:
        dff0s = roi.dttrialdff0s
    n_panes = condition.info.get('focal_pane_args', {}).get('n', 1)
    pane_offset = workspace.cur_pane or 0

    ws_condition = condition # added for debugging JZ

    cfreq = workspace.condition.info['framerate'] / n_panes
    tfs = []
    trials = dff0s.filter_by(trial_blank=False, trial_flicker=False)
    for tf in condition.tfrequencies:
        tf_trials = trials.filter_by(
                trial_tf=tf,
                trial_contrast=trial_contrast,
                trial_sf=trial_sf
                )
        oris = []
        for ori in condition.orientations:
            reps_by_ori = tf_trials.filter_by(trial_ori=ori)
            arr = np.array([
                rep.value['on'][pane_offset::n_panes][int(1*cfreq):int(2*cfreq)]
            for rep in reps_by_ori])
            meantrace_for_ori = np.nanmean(arr, axis=0)
            oris.append(meantrace_for_ori.mean())
        tfs.append(np.array(oris))
    peak_tf_index = np.array(tfs).max(axis=1).argmax()
    peak_tf = condition.sfrequencies[peak_tf_index]
    mat = tfs[peak_tf_index]
    fit = SumOfGaussianFit(condition.orientations, mat)

    return fit.o_pref, peak_tf, peak_tf_index

