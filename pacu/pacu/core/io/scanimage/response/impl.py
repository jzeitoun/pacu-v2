import numpy as np

from pacu.core.io.scanimage.response.orientation import Orientation

# almost deprecated
class Response(object):
    def __init__(self, trace, orientations):
        self.trace = trace
        self.orientations = orientations
    @property
    def repetition(self): #TODO use Repetition class
        bss = [np.vstack(trace.array for trace in ori.baselines)
            for ori in self.orientations]
        ons = [np.vstack(trace.array for trace in ori.ontimes)
            for ori in self.orientations]
        bss_ons = np.array([bss, ons])
        n_reps, n_frames = bss_ons.shape[2:]
        bss_ons_interleaved = 1, 0, 2, 3
        bss_ons_merged = -1, n_reps, n_frames
        orientation_interleaved = 1, 0, 2
        orientation_merged = n_reps, -1
        traces = bss_ons.transpose(
            *bss_ons_interleaved
        ).reshape(
            bss_ons_merged
        ).transpose(
            *orientation_interleaved
        ).reshape(
            orientation_merged
        )
        return dict(traces=traces,
            mean=traces.mean(axis=0), indices=self.orientation_indices(n_frames))
    def orientation_indices(self, n_frames):
        return {int((index*2+1.5)*n_frames): ori.value
            for index, ori in enumerate(self.orientations)}
    def toDict(self):
        return dict(
            trace = self.trace,
            repetition = self.repetition)

# from pacu.core.io.scanimage.impl import ScanimageIO
# test = ("/Volumes/Gandhi Lab - HT/Dario/2014.12.20/x.140801.1/"
#         "field004.imported")
# self = ScanimageIO(test).with_session('main').with_channel()
# roi = self.session.search('roi')[0]
# trace = roi.trace(self.channel.mmap)
# r = Response(
#     trace = trace,
#     orientations = [
#         Orientation.from_adaptor(ori, trace, self.db)
#         for ori in self.db.locator.orientations.loop()
#     ]
# )
