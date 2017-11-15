import ujson
from tornado.websocket import WebSocketHandler
# import numpy as np
import matplotlib.pyplot as plt

from pacu.core.scanbox import adapter
from pacu.core.scanbox import FileGroup as Scanbox

# mm = '/Volumes/Users/ht/Desktop/tiff.npy.bin'
# mm = np.memmap(mm, shape=(1024, 512, 512))
# asd = spec.get_meta('/Volumes/Users/ht/tmp/pysbx-data/JZ5/JZ5_000_003')
# mm2 = asd.raw.memmap[..., 0].view('uint8')[..., 1::2]
# data = dict(
#     flame = mm, sbx = mm2
# )

class MMWStreamHandler(WebSocketHandler):
    """
    Memory Mapped Web Socket Handler
    """
    meta = None
    url = r'/mmw-stream/(?P<uid>.+)'
    @classmethod
    def as_spec(cls):
        return cls.url, cls,
    def check_origin(self, origin):
        return True
    def on_message(self, message):
        print 'on_message', message
        packet = ujson.loads(message)
        getattr(self, packet['func'])(**packet)
    def open(self, uid):
        print 'open', uid
        if uid == 'undefined':
            return self.on_undefined()
        self.meta = adapter.get_meta(uid)
        self.metadata = self.meta.export()
        self.filename = self.meta.raw.filename
        self.memmap = self.meta.raw.memmap[..., 0].view('uint8')[..., 1::2]
        self.first_frame = self.memmap[0]
    def on_undefined(self):
        self.close()
    def on_close(self):
        """
        self.close_code
        self.close_reason
        """
    def init_resource(self, **kwargs):
        # self.cm = getattr(plt.cm, packet['colormap'])
        self.set_colormap()
        self.write_message(dict(
            func = 'ready',
            shape = self.memmap.shape,
            meta = self.metadata,
            filename = self.filename
        ))
    def set_colormap(self, cmap='gray', **kwargs):
        self.cm = getattr(plt.cm, cmap)
    def draw(self, index=0, **kwargs):
        frame = self.cm(~self.memmap[index], bytes=True).tostring()
        self.write_message(frame, binary=True)
