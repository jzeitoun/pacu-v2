from __future__ import absolute_import

from pacu.core.andor.error import ZylaException
from pacu.core.andor.ctypes.library import ctypes
from pacu.core.andor.ctypes.define import AT_64, AT_INT, AT_U8P, AT_U8
from pacu.core.andor.acquisition.base import BaseAcquisition
from pacu.core.andor.acquisition import helper

INFINITE = 0xFFFFFFFF
FIVE_SECONDS = 1000*5
CHUNK_OFFSET = 4
CID_OFFSET = 8

class ZylaAcquisition(BaseAcquisition):
    def __call__(self):
        if self.inst.camera_acquiring:
            print 'AcquisitionStop'
            self.inst.handle.command(u'AcquisitionStop')
            self.inst.handle.core('Flush')
        else:
            print 'AcquisitionStart'
            self.inst.meta.cycle_mode.show()
            self.inst.meta.frame_count.show()
            self.inst.meta.metadata_enable.show()
            self.inst.handle.command(u'AcquisitionStart')
        return self
    def __enter__(self):
        if not self.inst.camera_acquiring:
            self.inst.meta.cycle_mode.show()
            self.inst.meta.frame_count.show()
            self.inst.meta.metadata_enable.show()
            self.inst.handle.command(u'AcquisitionStart')
        return self
    def __exit__(self, type, value, tb):
        if self.inst.camera_acquiring:
            self.inst.handle.command(u'AcquisitionStop')
            self.inst.handle.core('Flush')
    def alloc_buffer(self, size=None):
        size = size or self.inst.image_size_bytes
        return (AT_U8 * size)()
    def queue_buffer(self, requeue=None):
        size = self.inst.image_size_bytes
        buf = requeue or self.alloc_buffer(size)
        self.inst.handle.core('QueueBuffer', buf, size)
        return buf
    def wait_buffer(self, timeout=INFINITE, matching_buf=None):
        size = AT_INT()
        buf = AT_U8P()
        self.inst.handle.core('WaitBuffer', ctypes.byref(buf),
                ctypes.byref(size), timeout)
        if matching_buf:
            addr_same = ctypes.addressof(matching_buf) == ctypes.addressof(buf.contents)
            size_same = self.inst.image_size_bytes == size.value
            if addr_same and size_same:
                return buf
            else:
                raise ZylaException('Result of between Queuebuffer and WaitBuffer is mismatch.')
        return buf, size
    def convert_buffer(self, buf_src, buf_dst):
        self.inst.handle.util(u'ConvertBuffer',
            buf_src, buf_dst,
            AT_64(self.inst.aoi_width),
            AT_64(self.inst.aoi_height),
            AT_64(self.inst.aoi_stride),
            unicode(self.inst.pixel_encoding),
            u'Mono16')
        return buf_dst
    def extract_timestamp(self, buf):
        chunk_len = helper.offset_pointer(buf, len(buf) - CHUNK_OFFSET)
        cid = helper.offset_pointer(buf, len(buf) - CID_OFFSET)
        if cid == 1:
            return helper.offset_pointer(buf, len(buf) - CHUNK_OFFSET - chunk_len)
    def capture(self, timeout=FIVE_SECONDS):
        if not self.inst.camera_acquiring:
            raise ZylaException('The camera is not in acquisition mode.')
        raw = self.queue_buffer()
        buf = self.wait_buffer(timeout, matching_buf=raw)
        ts = self.extract_timestamp(raw)
        frame, pointer = helper.get_contigious(self.inst.aoi_height, self.inst.aoi_width)
        self.convert_buffer(buf, pointer) # fills `frame` (which `pointer` refers)
        return ts, frame
    # DEPRECATED - DOES NOT WORK
    # def burst(self, counts, timeout=FIVE_SECONDS):
    #     rawbufs = [self.queue_buffer() for c in range(counts)]
    #     bufs = [self.wait_buffer(timeout, matching_buf=rawbuf) for rawbuf in rawbufs]
    #     tss = [self.extract_timestamp(rawbuf) for rawbuf in rawbufs]
    #     frames, pointers = zip(*[helper.get_contigious(self.inst.aoi_height, self.inst.aoi_width) for rawbuf in rawbufs])
    #     _ = [self.convert_buffer(buf, pointer) for buf, pointer in zip(bufs, pointers)]
    #     return tss, frames
