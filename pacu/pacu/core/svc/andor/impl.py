import atexit
import tifffile
import numpy as np
import matplotlib.pyplot as plt

from pacu.core.andor.ctypes.library import ctypes
from pacu.core.andor.ctypes.callback import c_feat_cb
from pacu.core.andor.instrument.zyla import ZylaInstrument
from pacu.core.andor.instrument.system import SystemInstrument
from pacu.core.andor.acquisition import helper
from pacu.core.andor.feature import test
from pacu.core.svc.andor import handler
from pacu.core.handler import msg
from pacu.core.svc.andor.handler.bypass import BypassHandler
from pacu.core.svc.andor.handler.writer import WriterHandler
from pacu.core.svc.andor.handler.writer_by_ttl import WriterByTTLHandler

# non-streaming
# from u3 import U3, Counter0, Counter1
# u3 = U3(debug=False)
# u3.configIO(TimerCounterPinOffset=4, NumberOfTimersEnabled=0,
#     EnableCounter0=False, EnableCounter1=False, FIOAnalog=0)
# atexit.register(u3.close)
# counter0 = Counter0()
# counter1 = Counter1()
# def fire(pin=0):
#     u3.setFIOState(pin, 1)
#     u3.setFIOState(pin, 0)
# def cnt():
#     c1, c2 = u3.getFeedback(counter0, counter1)
#     print c1, c2

# exposure_time = 0.001 # 0.0001 makes fixed frame rate range
# trigger_mode = 0 # internal, just run
# trigger_mode = 1 # no user for zyla
# trigger_mode = 2 # External Start, run when contnues
# trigger_mode = 3 # External Exposure Triggering tick-wise granular
# trigger_mode = 4 # software trigger, no run when continues cycle
# trigger_mode = 6 # Exteral, tick tick tick fire-wise framing
# overlap = 0 # if 1, takes start end at once. if 0, take start and end sequentially
# overlap also unwritable when triggermode is 4, software, 6,external

class AndorBindingService(object):
    frame_gathered = 0
    _current_frame = None
    inst = None
    handler = None
    bypass = False
    # very rough and magic implementation.
    # no reason to be `files` argument.
    def __init__(self, files=-1):
        self.index = int(files)
    def __dnit__(self):
        print 'prepare to be destroyed...'
        try:
            msg.gets['svc.andor.on_external'].remove(self)
        except:
            pass
        if self.inst and self.inst.camera_acquiring:
            print 'stop acquiring...'
            self.stop_recording()
        try:
            print 'handle...',
            self.release_handle()
        except:
            print 'already released'
        else:
            print 'handle released'
    def acquire_handle(self):
        print 'Acquire camera handle...'
        # return True
        try:
            self.inst = SystemInstrument().acquire(ZylaInstrument, self.index)
        except Exception as e:
            raise Exception('Failed to acquire camera: ' + str(e))
        self.inst.aoi_height = 512
        self.inst.aoi_width = 512
        self.inst.accumulate_count = 4
        self.inst.frame_rate = 30.0
        self.inst.exposure_time = 0.01
        self.inst.cycle_mode = 1 # continuous
        self.inst.electronic_shuttering_mode = 1 # global
        self.inst.metadata_enable = 1
        self.inst.simple_preamp_gain_control = 2 # 16bit !important
        self.inst.vertically_centre_aoi = 0 # !important

        return True
    def release_handle(self):
        print 'Release camera handle...'
        # return None
        if self.inst and self.inst.camera_acquiring:
            raise Exception('Camera is in recording session. Stop first...')
        try:
            self.inst.release()
        except Exception as e:
            raise e
        else:
            self.inst = None
            self.handler = None
            return None
    @property
    def features(self):
        # return test.features
        try:
            return [self.inst.meta[key].export()
                for key in list(self.inst.feat)]
        except:
            return []
    def set_bypass(self, bypass):
        self.bypass = bypass
        if bypass:
            self.dump_socket('notify', 'Bypass on...')
        else:
            self.dump_socket('notify', 'Bypass off...')
    def set_handler(self, clsname, *args):
        if self.inst and self.inst.camera_acquiring:
            raise Exception('Camera is in recording session. Stop first...')
        self.handler = getattr(handler, clsname)(self, *args)
    def set_features(self, kwargs):
        for key, val in kwargs.items():
            try:
                self.set_feature(key, val)
            except Exception as e:
                print e
    def set_feature(self, key, val):
        # print 'SET FEATURE', key, val
        try:
            # for f in test.features:
            #     if f['key'] == key: f['value'] = val
            # return
            getattr(self.inst.meta, key).coerce(val)
        except Exception as e:
            raise Exception('Failed to update value: ' + str(e) + '({}: {})'.format(key, val))
    def start_recording(self, from_external=False):
        if self.handler:
            if isinstance(self.handler, WriterHandler) and not from_external:
                raise Exception('Recording can be started only from external signal.')
            else:
                self.handler.ready()
        else:
            raise Exception('Handler has not been assigned.')
        if not self.inst:
            raise Exception('Could not find camera.')
        if self.inst.camera_acquiring:
            raise Exception('Camera is still in recording session.')
        self.handler.enter()
        self.handler.register()
        for item in self.inst.feat.items():
            print item
        self.inst.acquisition()
        return True
    def stop_recording(self):
        if not self.handler:
            raise Exception('Handler has gone.')
        if not self.inst:
            raise Exception('Could not find camera.')
        if not self.inst.camera_acquiring:
            raise Exception('Camera is not in recording session.')
        self.inst.acquisition()
        self.handler.rollback()
        self.handler.exit()
        return None
    def set_cmap(self, name):
        self.cmap = getattr(plt.cm, name)
    cmap = plt.cm.gray # jet, hot, hsv
    @property
    def current_frame(self):
        frame = self.handler._current_frame
        if frame is not None:
            return self.cmap(frame.view('uint8')[1::2, ...], bytes=True).tostring()
    def enter_on_air(self):
        if self.inst and self.inst.camera_acquiring:
            return
        if not self.handler:
            raise Exception('Handler is not currently configured. Please setup first...')
        if isinstance(self.handler, WriterHandler):
            if self.on_external not in msg.gets['svc.andor.on_external']:
                msg.gets['svc.andor.on_external'].append(self.on_external)
                return 'Listening to external stimulus signal...stand by...'
    def exit_on_air(self):
        if self.inst and self.inst.camera_acquiring:
            return 'Acquisition will keep going...'
        if isinstance(self.handler, WriterHandler):
            try:
                msg.gets['svc.andor.on_external'].remove(self)
            except Exception as e:
                pass
            else:
                return 'End listening to stimulus signal...'
    def on_external(self, handler, protocol, *args, **kwargs):
        """
        curl host:port/msg/svc.andor.on_external/{protocol}/arg/.../arg?kw=arg&...
        """
        try:
            rv = getattr(self, 'protocol_%s' % protocol)(*args, **kwargs)
            handler.write(dict(data=rv, error=None))
        except Exception as e:
            print 'error on external communication: {}: {}: {}'.format(
                protocol, str(type(e)), str(e))
            error = dict(type=type(e).__name__, msg=str(e))
            handler.write(dict(data=None, error=error))
    def protocol_state_check(self):
        EXTERNAL_NA, EXTERNAL_READY = range(2)
        is_cont = self.inst.cycle_mode == 1
        is_ext = self.inst.trigger_mode == 6
        # print self.inst.cycle_mode, '< Cycle', is_cont
        # print self.inst.trigger_mode, '< Trigger', is_ext
        if is_cont and is_ext:
            if isinstance(self.handler, WriterHandler):
                return EXTERNAL_READY
            else:
                self.dump_socket('notify', None, 'Handler setup is not for external mode.')
        else:
            self.dump_socket('notify', None, 'Mode setup is not for external mode.')
        return EXTERNAL_NA
    def protocol_sync_metadata(self, member, filedir, filename):
        SYNC_FAIL = 0
        SYNC_SUCCESS = 1
        if self.handler.sync_name(member, filedir, filename):
            self.dump_socket('notify',
                'Recording location: %s' % self.handler.tifpath.str)
            return SYNC_SUCCESS
        else:
            return SYNC_FAIL
    def protocol_open(self):
        OPEN_FAIL = 0
        OPEN_SUCCESS = 1
        self.dump_socket('notify', 'Try to start recording...Preview will not update.')
        try:
            if self.start_recording(from_external=True):
                return OPEN_SUCCESS
            else:
                return OPEN_FAIL
        except Exception as e:
            self.dump_socket('notify', None, str(e))
            raise e
    def protocol_close(self):
        CLOSE_FAIL = 0
        CLOSE_SUCCESS = 1
        self.dump_socket('notify', 'Try to stop recording...')
        try:
            if self.stop_recording(): # return None when normal
                return CLOSE_FAIL
            else:
                return CLOSE_SUCCESS
        except Exception as e:
            self.dump_socket('notify', None, str(e))
            raise e
    def dump_socket(self, seq, arg, err=None):
        sc = self.__socket__
        if sc:
            sc.dump_message(seq, arg, err)
