__package__ = '' # unicode package name error

import numpy as np

from pacu.core.io.scanbox.method.fit.sogfit import SumOfGaussianFit

# not used any more, have to find peak sf from mean responses
# def main(workspace, condition, roi, datatag, dff0s=None):
#     if not dff0s:
#         dff0s = roi.dttrialdff0s
#     n_panes = condition.info.get('focal_pane_args', {}).get('n', 1)
#     pane_offset = workspace.cur_pane or 0
# 
#     cfreq = workspace.condition.info['framerate'] / n_panes
#     sfs = []
#     trials = dff0s.filter_by(trial_blank=False, trial_flicker=False)
#     for sf in condition.sfrequencies:
#         sf_trials = trials.filter_by(trial_sf=sf,
#             trial_contrast=datatag.trial_contrast)
#         oris = []
#         for ori in condition.orientations:
#             reps_by_ori = sf_trials.filter_by(trial_ori=ori)
#             arr = np.array([
#                 rep.value['on'][pane_offset::n_panes][int(1*cfreq):int(2*cfreq)]
#             for rep in reps_by_ori])
#             meantrace_for_ori = np.nanmean(arr, axis=0)
#             oris.append(meantrace_for_ori)
#         sfs.append(np.array(oris))
#     mat = np.nanmean(np.array(sfs), axis=(0,2))
#     fit = SumOfGaussianFit(condition.orientations, mat)
#     return fit.o_pref

def main(workspace, condition, roi, datatag, dff0s=None):
    if not dff0s:
        dff0s = roi.dttrialdff0s
    n_panes = condition.info.get('focal_pane_args', {}).get('n', 1)
    pane_offset = workspace.cur_pane or 0

    ws_condition = condition # added for debugging JZ

    cfreq = workspace.condition.info['framerate'] / n_panes
    sfs = []
    trials = dff0s.filter_by(trial_blank=False, trial_flicker=False)
    for sf in condition.sfrequencies:
        if datatag.trial_tf:
            sf_trials = trials.filter_by(
                    trial_sf=sf,
                    trial_contrast=datatag.trial_contrast,
                    trial_tf=datatag.trial_tf # added by JZ
                    )
        else:
            sf_trials = trials.filter_by(
                    trial_sf=sf,
                    trial_contrast=datatag.trial_contrast,
                    )
        oris = []
        for ori in condition.orientations:
            reps_by_ori = sf_trials.filter_by(trial_ori=ori)
            arr = np.array([
                rep.value['on'][pane_offset::n_panes][int(1*cfreq):int(2*cfreq)]
            for rep in reps_by_ori])
            meantrace_for_ori = np.nanmean(arr, axis=0)
            oris.append(meantrace_for_ori.mean())
        sfs.append(np.array(oris))
    peak_sf_index = np.array(sfs).max(axis=1).argmax()
    peak_sf = condition.sfrequencies[peak_sf_index]
    mat = sfs[peak_sf_index]
    fit = SumOfGaussianFit(condition.orientations, mat)
    return fit.o_pref, peak_sf, peak_sf_index

if __name__ == '__sbx_main__':
    value, peak_sf, peak_sf_index = main(workspace, condition, roi, datatag)
    datatag.value = value
    datatag.peak_sf = peak_sf
    datatag.peak_sf_index = peak_sf_index

if __name__ == '__sbx_stitch__':
    value, peak_sf, peak_sf_index = main(workspace, condition, roi, datatag, dff0s)
    datatag.value = value
    datatag.peak_sf = peak_sf
    datatag.peak_sf_index = peak_sf_index
# cfreq = adaptor.capture_frequency
# return np.array([
#     resp.orientations.ons[...,
#     int(1*cfreq):int(2*cfreq)
# ].mean(axis=(1, 2)) for sf, resp in self.sorted_responses]).mean(axis=0)
