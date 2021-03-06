__package__ = '' # unicode package name error

import numpy as np
from pacu.core.io.scanbox.method.bootstrap.fit import Bootstrap
import random

bound_dtype = [('val', float), ('ori', float)]

def bind(trials_by_sf, oris, cfreq):
    windowed = [[
        np.array(trial.value['on'])[int(1*cfreq):int(2*cfreq)].mean()
        for trial in trials_by_sf.filter_by(trial_ori=ori)
    ] for ori in oris]
    mat = [
        [(value, ori) for value in values]
        for values, ori in zip(windowed, oris)
    ]
    return np.array(mat, dtype=bound_dtype).T

def main(workspace, condition, roi, datatag):
    cfreq = condition.info.get('framerate')
    oris = condition.orientations
    sfs = condition.sfrequencies

    dts = roi.datatags.filter_by(trial_blank=False, trial_flicker=False)
    bls = roi.datatags.filter_by(method='dff0', trial_blank=True)
    fls = roi.datatags.filter_by(method='dff0', trial_flicker=True)

    # If blank/flicker conditions are absent, off periods from random
    # set of trials is used (JZ)
    reps = condition.repetition
    num_trials = len(dff0s)

    if not bls:
        blank_trial_indices = random.sample(xrange(0, num_trials), reps)
        bls = [dff0s[i] for i in blank_trial_indices]
        blank = np.array([[bl.value['baseline']] for bl in bls]).mean(0).mean()
    else:
        blank = np.array([[bl.value['on']] for bl in bls]).mean(0).mean()

    if not fls:
        flicker_trial_indices = random.sample(xrange(0, num_trials), reps)
        fls = [dff0s[i] for i in flicker_trial_indices]
        flicker = np.array([[bl.value['baseline']] for fl in fls]).mean(0).mean()
    else:
        flicker = np.array([[bl.value['on']] for fl in fls]).mean(0).mean()


    bound_response = np.concatenate(
        [bind(dts.filter_by(trial_sf=sf), oris, cfreq) for sf in sfs], axis=1)
    return Bootstrap(bound_response, flicker, blank, sfs).run().toDict()

if __name__ == '__sbx_main__':
    datatag.value = main(workspace, condition, roi, datatag)
