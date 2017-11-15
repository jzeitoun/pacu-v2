import sys
import struct
import importlib
import contextlib
import traceback

import numpy as np

from pandas import json
from pacu.ext.tornado import websocket

@contextlib.contextmanager
def print_captured(by): # should be `write` compatible
    sys.stdout = by
    try:
        yield by
    finally:
        sys.stdout = sys.__stdout__

def print_exc(e):
    info = sys.exc_info()
    source = traceback.format_exception(*info)
    print '\n======== exception on websocket delegation ========'
    traceback.print_exception(*info)
    print '======== exception on websocket delegation ========\n'

def handle_exc(e):
    print_exc(e)
    raise e

# currently web socket handler does not work in non-main thread
# thus shell mode does not support web socket in place.
class WSHandler(websocket.WebSocketHandler):
    """
    A Generic web socket handler.
      * `check_origin` returns always `True`.
    """
    url = r'/ws/(?P<modname>[\w\.]+)/(?P<clsname>[\w\.]+)'
    inst = None
    __socket__ = None
    def write(self, line):
        self.dump_message('print', line, None)
    def open(self, modname, clsname):
        print 'websocket is opening...'
        self.set_nodelay(True)
        kwargs = {key: val
            for key, vals in self.request.arguments.items()
            for val in vals}
        try:
            cls = getattr(importlib.import_module(modname), clsname)
        except ImportError as e:
            handle_exc(e)
        except AttributeError as e:
            handle_exc(e)
        try:
            self.inst = cls(**kwargs) if kwargs else cls
            self.inst.__socket__ = self
        except Exception as e:
            handle_exc(e)
    def on_close(self):
        print 'websocket is closing...'
        if hasattr(self.inst, '__dnit__'):
            self.inst.__dnit__()
        if self.inst:
            self.inst.__socket__ = None
    def access(self, route):
        attrs = route.split('.')
        value = reduce(getattr, attrs, self.inst)
        return value
    def invoke(self, route, args=None, kwargs=None):
        func = self.access(route)
        return func(*args or [], **kwargs or {})
    def on_message(self, message):
        rv, err = None, None
        try:
            seq, ftype, route, payload = json.loads(message)
            as_binary = payload.pop('as_binary')
            func = getattr(self, ftype)
            with print_captured(self):
                rv = func(route, **payload)
        except Exception as e:
            info = sys.exc_info()
            source = traceback.format_exception(*info)
            print '\n======== exception on websocket ========'
            traceback.print_exception(*info)
            print '======== exception on websocket ========\n'
            err = dict(
                title = e.__class__.__name__,
                detail = str(e),
                source = source
            )
        if as_binary and rv is not None:
            # two uint32 for seq and error, 8bytes in total
            # in network byte order (big endian)
            meta = struct.pack('!II', seq, 0) # 0 for err (temporary)
            self.write_message(meta + rv, binary=True)
        else:
            self.dump_message(seq, rv, err)
    def dump_message(self, seq, rv, err):
        try:
            dumped = json.dumps([seq, rv, err])
        except Exception as e: # coerce
            print 'Websocket coerces exception:'
            print_exc(e)
            dumped = json.dumps([seq, str(rv), err])
        self.write_message(dumped)
