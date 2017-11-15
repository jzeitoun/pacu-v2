import re
import os

import time
from tifffile import TiffWriter

from pacu.util.path import Path
from pacu.core.svc.andor.handler.base import BaseHandler
from pacu.util.compat import str

re_filename = re.compile(r'^\w+$')
users_desktop = Path(os.path.expanduser('~'), 'Desktop')
ip1_datapath = Path('D:', 'data')

class WriterHandler(BaseHandler):
    def sync_name(self, member, filedir, filename):
        path = ip1_datapath.joinpath(member, filedir)
        if not path.is_dir():
            os.makedirs(path.str)
        self.tifpath = path.joinpath(filename).with_suffix('.tif')
        self.csvpath = path.joinpath(filename).with_suffix('.csv')
        return True # self.ready()
    def check(self, filename):
        pass
    def ready(self):
        if self.tifpath.is_file() or self.csvpath.is_file():
            raise Exception('Filename already exists. Please provide new one...')
        else:
            return True
    def register(self):
        super(WriterHandler, self).register()
        self.ready_at = time.time()
    def enter(self):
        print 'enter'
        self.tif = TiffWriter(self.tifpath.str, bigtiff=True)
        self.csv = self.csvpath.open('w')
    def exposure_end(self, frame, _ts):
        if self.svc.bypass:
            return
        ts = time.time() - self.ready_at
        self.tif.save(frame)
        # self.tif.save(frame, extratags=[(
        #     306, 's', 0, str(ts), False
        # )])
        self.csv.write(u'{}\n'.format(ts))
    def exit(self):
        print 'exit'
        self.tif.close()
        self.csv.close()
