import numpy as np

from pacu.core.io.scanimage.roi.impl import ROI

def test_get_roi():
    polygon = [
        {u'y': 80, u'x': 63},
        {u'y': 74, u'x': 71},
        {u'y': 75, u'x': 79},
        {u'y': 85, u'x': 77},
        {u'y': 86, u'x': 68}]
    return ROI(polygon=polygon)
def test():
    np.random.seed(1234)
    frames = np.random.randint(0, 256*256, (64, 128, 128))
    return test_get_roi(), frames
def test_trace():
    pass
    # np.random.seed(1234)
    # contours = np.array([[point['x'], point['y']] for point in polygon])
    # frames = np.random.randint(0, 256*256, (64, 128, 128))
    # mask = np.ma.zeros(frames.shape[1:], dtype='uint8')
    # cv2.drawContours(mask, [contours], 0, 255, -1)
    # trace = np.array([cv2.mean(frame, mask)[0] for frame in frames])
