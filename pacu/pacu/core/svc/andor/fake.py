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

# So this is fake handler for debug and test when
# we have no Andor device setup locally
class FakeAndorBindingService(object):
    _msg_gets = msg.gets
    _msg_posts = msg.posts
    _current_frame = None
    frame_gathered = 0
    inst = None
    handler = None
    bypass = False
    # very rough and magic implementation.
    # no reason to be `files` argument.
    def __init__(self, files=-1):
        pass
    def __dnit__(self):
        print 'prepare to be destroyed...'
        try:
            msg.gets['svc.andor'].remove(self)
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
        return True
    def release_handle(self):
        print 'Release camera handle...'
        return None
    @property
    def features(self):
        return test.features
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
        print 'SET FEATURE', key, val
        for f in test.features:
            if f['key'] == key: f['value'] = val
        return
    def start_recording(self, from_external=False):
        pass
    def stop_recording(self):
        pass
    def set_cmap(self, name):
        pass
    cmap = plt.cm.gray # jet, hot, hsv
    @property
    def current_frame(self):
        pass
    def enter_on_air(self):
        pass
    def exit_on_air(self):
        pass
    def on_external(self, handler, protocol, *args, **kwargs):
        pass
    def protocol_state_check(self):
        pass
    def protocol_sync_metadata(self, member, filedir, filename):
        pass
    def protocol_open(self):
        pass
    def protocol_close(self):
        pass
    def dump_socket(self, seq, arg, err=None):
        sc = self.__socket__
        if sc:
            sc.dump_message(seq, arg, err)
    def set_bypass(self, bypass):
        self.bypass = bypass
        if bypass:
            self.dump_socket('notify', 'Bypass on...')
        else:
            self.dump_socket('notify', 'Bypass off...')
