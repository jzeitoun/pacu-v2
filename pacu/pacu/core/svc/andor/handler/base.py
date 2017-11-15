from weakref import WeakValueDictionary

from pacu.core.andor.ctypes.callback import c_feat_cb
from pacu.core.andor.acquisition import helper

CONTEXTS = WeakValueDictionary()

@c_feat_cb
def exposure_start(handle, feature, context):
    self = CONTEXTS[context]
    if not self.inst.camera_acquiring:
        return 0
    self.inst.acquisition.queue_buffer(self.rawbuf)
    self.exposure_start()
    return 0
@c_feat_cb
def exposure_end(handle, feature, context):
    self = CONTEXTS[context]
    if not self.inst.camera_acquiring:
        return 0
    try:
        buf = self.inst.acquisition.wait_buffer(3000, matching_buf=self.rawbuf)
    except:
        return 0
    ts = self.inst.acquisition.extract_timestamp(self.rawbuf)
    ts = self.inst.from_timestamp(ts)
    frame, pointer = helper.get_contigious(self.inst.aoi_height, self.inst.aoi_width)
    self.inst.acquisition.convert_buffer(buf, pointer)
    self._current_frame = frame
    self.frame_gathered += 1
    self.exposure_end(frame, ts)
    return 0
@c_feat_cb
def buf_overflow(handle, feature, context):
    self = CONTEXTS[context]
    if not self.inst.camera_acquiring:
        return 0
    self.buf_overflow()
    return 0

entry = [
    (0, u'ExposureStartEvent' , exposure_start),
    (1, u'ExposureEndEvent'   , exposure_end  ),
    (5, u'BufferOverflowEvent', buf_overflow  ),
]

class BaseHandler(object):
    rawbuf = None
    _current_frame = None
    frame_gathered = 0
    __ts_reset_pending__ = True
    def __init__(self, svc, *args):
        err = self.check(*args)
        if err:
            raise Exception(err)
        self.svc = svc
        self.inst = svc.inst
        self.context = id(self)
        CONTEXTS[self.context] = self
    def check(self, *args):
        return NotImplemented
    def _event_selecting(self, onoff):
        for selector, feature, callback in entry:
            self.inst.event_selector = selector
            self.inst.event_enable = onoff
            self.inst.handle.core(
                ('RegisterFeatureCallback' if onoff else 'UnregisterFeatureCallback'),
                feature, callback, self.context)
    def register(self):
        self.inst.timestamp_clock_reset()
        self._event_selecting(1)
        self.rawbuf = self.inst.acquisition.alloc_buffer()
    def rollback(self):
        self._event_selecting(0)
        self.rawbuf = None
    def ready(self):
        raise NotImplementedError
    def exposure_start(self):
        pass
        # print 's',
    def exposure_end(self, frame, ts):
        pass
        # print 'e',
    def buf_overflow(self):
        pass
        # print 'buf overflow!'
    def enter(self):
        pass
    def exit(self):
        pass
