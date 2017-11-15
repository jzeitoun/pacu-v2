import atexit
import time
import tifffile

import numpy as np

from pacu.core.andor.ctypes.library import ctypes
from pacu.core.andor.ctypes.callback import c_feat_cb
from pacu.core.andor.instrument.zyla import ZylaInstrument
from pacu.core.andor.instrument.system import SystemInstrument
from pacu.core.andor.acquisition import helper

# non-streaming
from u3 import U3, Counter0, Counter1
u3 = U3(debug=False)
u3.configIO(TimerCounterPinOffset=4, NumberOfTimersEnabled=0,
    EnableCounter0=False, EnableCounter1=False, FIOAnalog=0)
atexit.register(u3.close)
# counter0 = Counter0()
# counter1 = Counter1()
def fire(pin=0):
    u3.setFIOState(pin, 1)
    u3.setFIOState(pin, 0)
# def cnt():
#     c1, c2 = u3.getFeedback(counter0, counter1)
#     print c1, c2
si = SystemInstrument()
qwe = si.acquire(ZylaInstrument)
# frames = qwe.acquisition()
# frame = next(frames)
# frame = next(frames)
# frame = next(frames)

# context = 181818
# 
# # commented out
# # @c_feat_cb
# # def feat_changed(handle, feature, context):
# #     print '\n', 'CALLBACK: `{}` CHANGED!'.format(feature), context
# #     # print '\n', 'CALLBACK: `{}` => `{}`'.format(feature, cam.get(feature))
# #     return 0 # meaning callback handled successful.
# # context = ctypes.cast(ctypes.byref(ctypes.c_int(qwe.handle)), ctypes.c_void_p)
# # for feat in map(unicode,
# #     'AOIWidth AOIHeight AOIBinning ReadoutTime ImageSizeBytes ExposureTime AOIStride FrameRate CameraAcquiring'.split()):
# #     qwe.handle.core('RegisterFeatureCallback',
# #         feat,
# #         feat_changed,
# #         context
# #     )
qwe.exposure_time = 0.001 # 0.0001 makes fixed frame rate range
qwe.metadata_enable = 1
# qwe.trigger_mode = 1 # internal, just run
# qwe.trigger_mode = 4 # software trigger, no run when continues cycle
# qwe.trigger_mode = 2 # External Start, run when contnues
# qwe.trigger_mode = 3 # External Exposure Triggering tick-wise granular
qwe.trigger_mode = 6 # External, no wanting to control exposure time
# qwe.overlap = 0 # if 1, takes start end at once. if 0, take start and end sequentially
# overlap also unwritable when triggermode is 4, software, 6,external
qwe.cycle_mode = 0 # 0 for fixed 1 for contigious
qwe.frame_count = 100
qwe.electronic_shuttering_mode = 1 # global
qwe.aoi_height = 1024
qwe.aoi_width = 1024
rawbuf = qwe.acquisition.alloc_buffer()
f = open('deleteme.bin', 'wb')
@c_feat_cb
def exposure_start(handle, feature, context):
    if not qwe.camera_acquiring:
        return 0
    print 's',
    # qwe.acquisition.queue_buffer(rawbuf)
    return 0
@c_feat_cb
def exposure_end(handle, feature, context):
    if not qwe.camera_acquiring:
        return 0
    print 'e',
    st = time.time()
    # time.sleep(1)
    # f.write(rawbuf)
    # buf = qwe.acquisition.wait_buffer(3000, matching_buf=rawbuf)
    # ts = qwe.acquisition.extract_timestamp(rawbuf)
    # frame, pointer = helper.get_contigious(qwe.aoi_height, qwe.aoi_width)
    # qwe.acquisition.convert_buffer(buf, pointer)
    print 'conv latency', time.time() - st
    # print frame[:3]
    # tifffile.imsave('a.tiff', frame)
    return 0
@c_feat_cb
def buf_overflow(handle, feature, context):
    print 'buf overflowed. cancel everything'
    return 0

context = 18
qwe.event_selector = 0 #'ExposureStartEvent'
qwe.event_enable = 1
qwe.handle.core('RegisterFeatureCallback',
    u'ExposureStartEvent',
    exposure_start,
    context)
qwe.event_selector = 1 # 'ExposureEndEvent'
qwe.event_enable = 1
qwe.handle.core('RegisterFeatureCallback',
    u'ExposureEndEvent',
    exposure_end,
    context)
qwe.event_selector = 5 # 'BufferOverflowEvent'
qwe.event_enable = 1
qwe.handle.core('RegisterFeatureCallback',
    u'BufferOverflowEvent',
    buf_overflow,
    context)
frames = qwe.acquisition()

# # commented out
# # qwe.exposure_time = 0.005 # 0.0001 makes fixed frame rate range
# # qwe.frame_rate = 30
# # qwe.aoi_binning = 1
# # qwe.frame_count = 10 not writable when cyclemode is 1 (contigious)
# # cam = qwe.acquisition()
# # length = 512
# # print 'capturing', length
# # _, frames = zip(*[cam.capture() for i in range(length)])
# # print 'shaping'
# # stack = np.concatenate(frames).reshape(length, qwe.aoi_width, qwe.aoi_height)
# # print 'make tiff'
# # tifffile.imsave('a.tif', stack)
# # print 'done !'
# 
