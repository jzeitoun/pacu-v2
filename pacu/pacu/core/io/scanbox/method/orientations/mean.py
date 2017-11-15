__package__ = '' # unicode package name error

import functools
import numpy as np

def main(workspace, condition, roi, datatag, dff0s=None):
    if not dff0s:
        dff0s = roi.dttrialdff0s
    if datatag.trial_tf:
        trials = dff0s.filter_by(
            trial_sf=datatag.trial_sf,
            trial_contrast=datatag.trial_contrast,
            trial_tf=datatag.trial_tf, # added by JZ for temporal frequency
            trial_flicker=False, trial_blank=False)
    else:
        trials = dff0s.filter_by(
            trial_sf=datatag.trial_sf,
            trial_contrast=datatag.trial_contrast,
            trial_flicker=False, trial_blank=False)

    ws_condition = condition # added for debugging JZ

    n_panes = condition.info.get('focal_pane_args', {}).get('n', 1)
    pane_offset = workspace.cur_pane or 0

    # to follow datastructure of dff0, below is not the best
    framerate = condition.info['framerate'] / n_panes # have to do this
    on_frames = int(condition.on_duration * framerate)
    bs_frames = int(condition.off_duration * framerate) - 1

    cursor = 0
    indice = []
    for ori in condition.orientations:
        cursor = cursor + bs_frames
        indice.append(cursor)
        cursor = cursor + on_frames

#     for ori in condition.orientations: # for each ori
#         print ori
#         for trial in trials.filter_by(trial_ori=ori): # for each rep
#             # import ipdb; ipdb.set_trace()
#             print trial.trial_sequence,
#             # trial.value['baseline'] + trial.value['on']
#         print
    # first axis is orientation, second is each trial

    oris = [
        [
            (
                trial.value['baseline'][pane_offset::n_panes] +
                trial.value['on'][pane_offset::n_panes]
            )
            for trial in trials.filter_by(trial_ori=ori)
        ]
    for ori in condition.orientations]

    # first axis is each trial, second is orientations, third is baseline ~ ontime
    matrix = np.array(oris).transpose(1,0,2)
    # first axis is each trial, second is baseline ~ ontime over all orientations
    matrix = np.array(map(np.concatenate, matrix))
    meantrace = np.nanmean(matrix, axis=0)
    indices = dict(zip(indice, condition.orientations))
    # import ipdb; ipdb.set_trace();
    return matrix, meantrace, indices, on_frames, bs_frames

if __name__ == '__sbx_main__':
    matrix, meantrace, indices, on_frames, bs_frames = main(workspace, condition, roi, datatag)
    datatag.matrix = matrix.tolist()
    datatag.meantrace = meantrace.tolist()
    datatag.indices = indices
    datatag.on_frames = on_frames
    datatag.bs_frames = bs_frames

if __name__ == '__sbx_stitch__':
    matrix, meantrace, indices, on_frames, bs_frames = main(workspace, condition, roi, datatag, dff0s)
    datatag.matrix = matrix.tolist()
    datatag.meantrace = meantrace.tolist()
    datatag.indices = indices
    datatag.on_frames = on_frames
    datatag.bs_frames = bs_frames

