import os

import atexit
import time

from u3 import U3
from tifffile import TiffWriter

# u3.configIO(TimerCounterPinOffset=4, NumberOfTimersEnabled=0,
#     EnableCounter0=False, EnableCounter1=False, FIOAnalog=0)
# atexit.register(u3.close)

# while 1:
#     print time.time(), 'FIO6:', u3.getFIOState(6)
#     time.sleep(0.1)

from pacu.util.path import Path
from pacu.core.svc.andor.handler.base import BaseHandler

class Chunk(object):
    """
    when the app is off: 0
    when app is on: 1
    when maze on refresh: 0
    """
    tif = None
    csv = None
    prev_state = None # should be neither True nor False
    open_state = False # but app's initial state was designed to be 1
    def __init__(self, path, u3, did_refresh):
        self.path = path
        self.u3 = u3
        self.did_refresh = did_refresh
        # to have initial chunk
        self.close()
        self.nudge_path()
        self.open()
        self.did_refresh(self.tifpath)
    def tick(self):
        state = self.u3.getFIOState(6)
        if self.prev_state is state: # same state
            if state: # is rising
                pass # self.open_state = True
            else: # is falling
                pass # self.open_state = False
        else: # new state
            # could write simpler code, future me will be suffering
            if state: # is rising
                self.open_state = True
            else: # is falling
                self.open_state = False
                self.refresh()
        self.prev_state = state
    def save(self, frame):
        if not self.open_state:
            return
        self.tif.save(frame)
        self.csv.write(u'{}\n'.format(time.time()))
    def refresh(self):
        self.close()
        self.nudge_path()
        self.open()
        self.did_refresh(self.tifpath)
    def open(self):
        self.tif = TiffWriter(self.tifpath.str, bigtiff=True)
        self.csv = self.csvpath.open('w')
    def nudge_path(self):
        self.tifpath = self.path.joinpath('{}.tif'.format(time.time()))
        self.csvpath = self.path.joinpath('{}.csv'.format(time.time()))
    def close(self):
        if self.tif:
            self.tif.close()
        if self.csv:
            self.csv.close()
        self.is_rising = False
    def did_refresh(self, tifpath):
        pass

class WriterByTTLHandler(BaseHandler):
    u3 = U3(debug=False, autoOpen=False)
    def check(self, basedir):
        self.basedir = basedir
    def make_path(self):
        now = time.strftime('%Y-%m-%dT%H-%M-%S', time.localtime())
        self.path = Path(self.basedir, now)
        try:
            os.makedirs(self.path.str)
        except Exception as e:
            raise Exception('Failed creating a base directory: ' + str(e))
    def ready(self):
        self.svc.dump_socket('notify', 'Opening TTL device...')
        try:
            self.u3.open()
        except:
            self.svc.dump_socket('notify', None, 'Could not open TTL device...')
    def enter(self):
        try:
            self.make_path()
            self.chunk = Chunk(self.path, self.u3, did_refresh=self.did_refresh)
        except:
            self.exit()
    def exit(self):
        self.svc.dump_socket('notify', 'Closing TTL device...')
        self.u3.close()
        self.chunk.close()
        self.chunk = None
    def exposure_start(self):
        self.chunk.tick()
    def exposure_end(self, frame, _ts):
        if self.svc.bypass:
            return
        self.chunk.save(frame)
    def did_refresh(self, tifpath):
        self.svc.dump_socket('notify',
            'Chunk created at {}.'.format(tifpath.str))
