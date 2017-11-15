__package__ = '' # unicode package name error

import numpy as np

from pacu.core.io.scanimage import util
from pacu.core.io.scanbox.method.fit.sogfit import SumOfGaussianFit

# SORT SORT SORT SORT SORT SORT SORT SORT SORT SORT SORT SORT SORT
# DID YOU SORT DATTAG?
# self.CV = getCV(meanresponses=self.meanresponses, angles=c['orientations'])

sog_default = dict(
    a1_min = 0,
    a1_max = 0.5,
    a2_min = 0,
    a2_max = 0.5,
    sigma_min = 15,
    sigma_max = 60,
    offset_min = 0,
    offset_max = 0.01,
    use_seed = False,
    override = False,
)

PATTRS = 'a1min a1max a2min a2max sigmin sigmax offmin offmax'.split()

def main(workspace, condition, roi, datatag, dff0s=None, bestprefs=None):
    if not dff0s:
        dff0s = roi.dttrialdff0s
    n_panes = condition.info.get('focal_pane_args', {}).get('n', 1)
    pane_offset = workspace.cur_pane or 0
    if datatag.trial_tf:
        trials = dff0s.filter_by(
            trial_sf=datatag.trial_sf,
            trial_contrast=datatag.trial_contrast,
            trial_tf=datatag.trial_tf, # added by JZ
            trial_blank=False,
            trial_flicker=False,
        )
    else:
        trials = dff0s.filter_by(
            trial_sf=datatag.trial_sf,
            trial_contrast=datatag.trial_contrast,
            trial_blank=False,
            trial_flicker=False,
        )

    if not bestprefs:
        bestprefs = roi.dtorientationbestprefs
    best_pref = bestprefs.filter_by(
        trial_contrast=datatag.trial_contrast).first
    best_pref_ori = best_pref.value
    oris = []

    # this is where response for given orientation and sf is made
    for ori in condition.orientations:
        reps_by_ori = trials.filter_by(trial_ori=ori)
        arr = np.array([rep.value['on'][pane_offset::n_panes] for rep in reps_by_ori])
        meantrace_for_ori = np.nanmean(arr, axis=0)
        oris.append(meantrace_for_ori)
    mat = np.nanmean(np.array(oris), axis=1)
    params = datatag.sog_params or sog_default

    # Patched to use auto-selection of max amplitudes based off the max of the average response across orientations. (JZ)
    if not params['override']:
        params['a1_max'] = max(mat) if max(mat) > 0 else 0
        params['a2_max'] = max(mat) if max(mat) > 0 else 0
        params['sigma_min'] = 180 / len(condition.orientations)

    if params['use_seed']:
        peak_sf_index = best_pref.peak_sf_index
        if not peak_sf_index:
            print 'Peak Spatial Frequency information not found. Try refresh...'
            best_pref.refresh()
            peak_sf_index = best_pref.peak_sf_index
        seed = mat[peak_sf_index]
        print 'Fitting SoG using a seed value...'
        print 'Peak SF Index is {}, Value is {}'.format(peak_sf_index, seed)
        params['a1_max'] = seed
        params['a2_max'] = seed

    # p = roi.sog_initial_guess or workspace.sog_initial_guess
    # a1m, a1M, a2m, a2M, sm, sM, om, oM = [p[attr] for attr in PATTRS]
    fit = SumOfGaussianFit(condition.orientations, mat, best_pref_ori, (
        (params['a1_min']   , params['a1_max']),
        (params['a2_min']   , params['a2_max']),
        (params['sigma_min'], params['sigma_max']),
        (params['offset_min'], params['offset_max'])
    ))
    return util.nan_for_json(dict(
        orientations = condition.orientations,
        osi = fit.osi,
        dsi = fit.dsi,
        cv = fit.cv,
        dcv = fit.dcv, # added by (JZ)
        sigma = fit.sigma,
        o_pref = fit.o_pref,
        r_max = fit.r_max,
        residual = fit.residual,
        x = fit.stretched.x.tolist(),
        y_meas = fit.stretched.y.tolist(),
        y_fit = fit.y_fit.tolist()))

if __name__ == '__sbx_main__':
    datatag.value = main(workspace, condition, roi, datatag)

if __name__ == '__sbx_stitch__':
    datatag.value = main(workspace, condition, roi, datatag, dff0s, bestprefs)
