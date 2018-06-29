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
    roi_id_map = {roi.id: roi for roi in ws.rois}
    for roi in rois:
        if 'trace' not in roi:
            continue
        trace = np.array(roi['trace'])
        db_roi = roi_id_map[roi['roi_id']]
        for trial in db_roi.dttrialdff0s:
            indices = get_trial_indices(workspace, condition, trial)
            trial.value['baseline'] = trace[slice(*indices['baseline'])]
            trial.value['on'] = trace[slice(*indices['on'])]
        print('Updated trace for ROI {}'.format(roi['roi_id']))
    io.db_session.flush() # Commit updates
