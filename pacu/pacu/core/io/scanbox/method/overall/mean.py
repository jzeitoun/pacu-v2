__package__ = '' # unicode package name error

import numpy as np
from pacu.core.io.scanbox.method.overall.tracer import ROITracer

def main(workspace, condition, roi, datatag):
    # possible unnecessary db connection?
    channel = condition.io.ch0
    channel.c_focal_pane = workspace.cur_pane or 0
    frames = channel._mmap # take the entire trace
    tracer = ROITracer(roi, frames)
    if roi.neuropil_enabled: # np goes first to get cache benefit because
                             # np has larger area than normal
        print 'NP enabled, NP first'
        np_trace = tracer.neuropil_trace(workspace.other_rois(roi))
        main_trace = tracer.trace()
        main_trace -= np_trace * roi.neuropil_factor
    else:
        main_trace = tracer.trace()
    shift = workspace.params.frame_shift
    print 'Roll array by', shift
    main_trace = np.roll(main_trace, shift)
    return main_trace.tolist()

if __name__ == '__sbx_main__':
    datatag.value = main(workspace, condition, roi, datatag)
