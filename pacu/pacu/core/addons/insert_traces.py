import numpy as np
import json

import sys
import os

from pacu.core.io.scanbox.method.trial.dff0 import get_trial_indices

def insert_traces(io, ws, rois):
    '''
    Updates each of the trial "dttrialdff0s" objects with the corresponding segment
    of the custom trace.
    '''
    condition = io.condition
    workspace = io.condition.workspaces.filter_by(name=ws.name)[0]
    roi_id_map = {roi.id: roi for roi in workspace.rois}
    for roi in rois:
        if 'trace' not in roi or roi['roi_id'] not in roi_id_map:
            continue
        trace = np.array(roi['trace'])
        db_roi = roi_id_map[roi['roi_id']]
        for trial in db_roi.dttrialdff0s[1:]:
            indices = get_trial_indices(workspace, condition, trial)
            baseline = trace[slice(*indices['baseline'])]
            on = trace[slice(*indices['on'])]
            trial.value = {'baseline': baseline.tolist(), 'on': on.tolist()}
        print('Updated trace for ROI {}'.format(roi['roi_id']))
    io.db_session.flush() # Commit updates
