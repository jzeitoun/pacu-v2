import math
import numpy.core.memmap as memmap
import matplotlib.pyplot as plt

from pacu.util.path import Path
from pacu.profile import manager
from pacu.core.io.scanbox.impl import ScanboxIO
from pacu.core.io.scanimage.impl import ScanimageIO
from pacu.core.io.scanbox.condition import ScanboxCondition
from pacu.core.io.scanimage.condition import ScanimageCondition
from pacu.core.model.ed.visstim2p import VisStim2P
from pacu.core.model.experiment import ExperimentV1
from pacu.core.model.analysis import AnalysisV1
from pacu.core.svc.analysis.i3d.twoway.roi import TwowayROI

# from pacu.core.method.twophoton.tuning.parse import Response
# from pacu.core.method.twophoton.frequency.spatial.meta import SpatialFrequencyMeta

DB = manager.get('db').as_resolved
# DB = manager.get('db').section('ephemeral')
ED = manager.get('db').section('ed')()

jet = getattr(plt.cm, 'jet')

class I3DAnalysisService(object):
    """
    imgstack instance should implement following methods and properties.
    @dimension(self)
    @max_index(self)
    request_frame(self, index)
    grand_trace(self)
    trace(self, x1, x2, y1, y2)

    and for condition instance...
    extract(self)
    """
    imgstack = None
    def debug(self):
        from ipdb import set_trace
        set_trace()
    def __init__(self, files=None): # analysis_v1 id will come in
        self.db, self.ed = DB(), ED()
        av1 = self.db.query(AnalysisV1).get(files)
        if av1.type == '0': # ScanImage
            vst = self.ed.query(VisStim2P).get(av1.conditionid)
            self.condition = ScanimageCondition(**vars(vst))
            self.imgstack = ScanimageIO(av1.imagesrc)
        else: # Scanbox
            vst = self.db.query(ExperimentV1).get(av1.conditionid)
            self.condition = ScanboxCondition(**vars(vst))
            self.imgstack = ScanboxIO(av1.imagesrc)
        self.av1 = av1
        # self.sfreq_meta = SpatialFrequencyMeta(self.condition)
    @property
    def dimension(self):
        return self.imgstack.dimension
    def request_frame(self, index):
        return self.imgstack.request_frame(index).tostring()
    def purge_roi(self):
        keys = [key for key in self.av1.data if key.startswith('roi.')]
        for key in keys:
            del self.av1.data[key]
        self.db.commit()
    def upsert_roi(self, data, *fields):
        roi = TwowayROI(**data)
        self.av1.data[roi.rid] = roi
        self.db.commit()
        return roi
    def delete_roi(self, rid):
        del self.av1.data[rid]
        self.db.commit()
    def fetch_roi_data(self, rid):
        roi = self.av1.data[rid]
        print rid, roi
        return dict(a=1)
    @property
    def rois(self):
        return [val for key, val in self.av1.data.items()
            if key.startswith('roi.')]
#    def get_grand_trace(self):
#        key = 'cache.grand_trace'
#        if key not in self.av1.data:
#            trace = self.imgstack.grand_trace()
#            self.av1.data[key] = trace.tolist()
#            self.db.commit()
#        return self.av1.data.get(key)
#    def get_current_sfrequency(self):
#        key = 'current_sfrequency'
#        if key not in self.av1.data:
#            self.av1.data[key] = 0
#            self.db.commit()
#        return self.av1.data.get(key)
#     def get_trace(self, x1, x2, y1, y2):
#         # self.get_trace(377, 426, 167, 219)
#         return self.imgstack.trace(x1, x2, y1, y2)
#         # return (~self.imgstack.io[:, y1:y2, x1:x2]).mean(axis=(1,2))
#     def get_response(self, x1, x2, y1, y2):
#         trace = self.get_trace(x1, x2, y1, y2)
#         try:
#             resp = Response(trace, self.condition, self.sfreq_meta)
#         except Exception as e:
#             raise Exception('Failed to get response: ' + str(e))
#         rv = dict(
#             OSI      = resp.OSI,
#             CV       = resp.CV,
#             DSI      = resp.DSI,
#             sigma    = resp.sigma,
#             OPref    = resp.Opref,
#             RMax     = resp.Rmax,
#             Residual = resp.Residual,
#         )
#         return {
#             key: "NaN" if math.isnan(val) else float(val)
#             for key, val in rv.items()
#         }
#     def resp(self, x1=0, x2=10, y1=0, y2=10):
#         trace = self.get_trace(x1, x2, y1, y2)
#         return Response(trace, self.condition, self.sfreq_meta)


# qwe = I3DAnalysisService(2)
















# example for scanimage
# qwe = I3DAnalysisService(2)

# get_ipython().magic('pylab')
# 
# import numpy as np
# from matplotlib.pyplot import *
# 
# qwe = I3DAnalysisService(14)
# start_times = qwe.condition.start_times
# response = qwe.resp(447, 475, 140, 166)
# # response = qwe.resp(461, 482, 247, 265)
# for i, ori in enumerate(response.orientations):
#     baseline_length = len(ori.meanbaseline_trace)
#     ori.baseline_seq = np.arange(baseline_length) + baseline_length*i*2
#     plot(ori.baseline_seq, ori.meanbaseline_trace, color='blue')
# 
#     response_length = len(ori.meantrace)
#     ori.response_seq = np.arange(response_length) + ori.baseline_seq[-1] + 1
#     plot(ori.response_seq, ori.meantrace, color='red')
# 
#     for rep in ori.reps:
#         plot(ori.baseline_seq, rep.baseline_trace, color='gray', linewidth=0.25)
#         plot(ori.response_seq, rep.trace, color='gray', linewidth=0.25)
# 
# xticks(*zip(*[(ori.baseline_seq[0], ori.name) for ori in response.orientations]))
# axis('auto')
# xlabel('orientation')
# ylabel('response')
# legend(['baseline', 'response'])
