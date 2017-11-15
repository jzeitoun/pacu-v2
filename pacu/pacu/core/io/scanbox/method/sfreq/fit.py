__package__ = '' # unicode package name error

import numpy as np

from pacu.core.io.scanbox.method.fit.dogfit import SpatialFrequencyDogFit
# did you sort datatag?
def main(workspace, condition, roi, datatag, dff0s=None, fits=None):
    n_panes = condition.info.get('focal_pane_args', {}).get('n', 1)
    pane_offset = workspace.cur_pane or 0
    if not dff0s:
        dff0s = roi.dttrialdff0s
    if not fits:
        fits = roi.dtorientationsfits
    if datatag.trial_tf:
        dts = fits.filter_by(trial_contrast=datatag.trial_contrast, trial_tf=datatag.trial_tf)
    else:
        dts = fits.filter_by(trial_contrast=datatag.trial_contrast)
    bls = dff0s.filter_by(trial_blank=True)
    fls = dff0s.filter_by(trial_flicker=True)
    sf_rmax_set = [(dt.trial_sf, dt.value['r_max']) for dt in dts]
    blank = np.nanmean(np.array([[bl.value['on'][pane_offset::n_panes]] for bl in bls]), axis=0).mean()
    flicker = np.nanmean(np.array([[fl.value['on'][pane_offset::n_panes]] for fl in bls]), axis=0).mean()
    fit = SpatialFrequencyDogFit(sf_rmax_set, flicker, blank)
    return fit.toDict()

if __name__ == '__sbx_main__':
    datatag.value = main(workspace, condition, roi, datatag)
# cutoff repvalue on [capture frq
if __name__ == '__sbx_stitch__':
    datatag.value = main(workspace, condition, roi, datatag, dff0s, fits)
