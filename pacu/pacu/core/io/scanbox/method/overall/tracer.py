import time
import cv2
import numpy as np

def trace_with_bounding_rect(frames, cnt, mask):
    x, y, w, h = cv2.boundingRect(np.array([cnt]))
    bounding_frames = frames[:, y:y+h, x:x+w]
    bonuding_mask = mask[y:y+h, x:x+w]
    # np.stack is really necessary?
    # also iterate over large arrays?
    # or custom mean algo?
    return np.array([cv2.mean(frame, bonuding_mask)[0]
        for frame in bounding_frames], dtype='float64')

class ROITracer(object):
    def __init__(self, roi, frames):
        self.roi = roi
        self.frames = frames
        self.shape = frames.shape[1:]
    def mask(self):
        mask = np.zeros(self.shape, dtype='uint8')
        cv2.drawContours(mask, [self.roi.contours], 0, 255, -1)
        return mask
    def neuropil_mask(self, others):
        mask = np.zeros(self.shape, dtype='uint8')
        cv2.drawContours(mask, [self.roi.neuropil_contours], 0, 255, -1)
        cv2.drawContours(mask, [self.roi.contours], 0, 0, -1)
        for other in others:
            cv2.drawContours(mask, [other.contours], 0, 0, -1)
        return mask
    # could we do below 2 jobs at once?
    def trace(self):
        mask = self.mask()
        s = time.time()
        # arr = np.stack(cv2.mean(frame, mask)[0] for frame in self.frames)
        arr = trace_with_bounding_rect(self.frames, self.roi.contours, mask)
        print 'ROI {} TRACING ELAPSED: {:0.3f}'.format(self.roi.id, time.time() - s)
        return arr
    def neuropil_trace(self, others):
        mask = self.neuropil_mask(others)
        s = time.time()
        # arr = np.stack(cv2.mean(frame, mask)[0] for frame in self.frames)
        arr = trace_with_bounding_rect(self.frames, self.roi.neuropil_contours, mask)
        print 'ROI {} NP TRACING ELAPSED: {:0.3f}'.format(self.roi.id, time.time() - s)
        return arr
