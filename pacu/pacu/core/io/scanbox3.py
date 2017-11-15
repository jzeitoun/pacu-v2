from __future__ import division

import numpy as np

from pacu.core.io.view.zero_dimension_array import ZeroDimensionArrayView
from pacu.util.path import Path
from pacu.util.prop.memoized import memoized_property

class Scanbox3IO(object):
    """
    locates directory
    dir/
        meta.mat
        mmap.npy?
    """
    # has mat
    # has sbx
    # others
    def __init__(self, path):
        self.path = Path(path) # without_suffixes '.mat', '.sbx'
    def __repr__(self):
        return '{}({!r})'.format(type(self).__name__, self.path.str)
    @property
    def matpath(self):
        return self.path.with_suffix('.mat')
    @property
    def sbxpath(self):
        return self.path.with_suffix('.sbx')
    @memoized_property
    def mat(self):
        return ZeroDimensionArrayView.from_mat(self.matpath.str)
    @memoized_property
    def sbx(self):
        return
    @memoized_property
    def mmap(self):
        pass


# print 'framerate', q.mat.resfreq / q.mat.recordsPerBuffer
# q = Scanbox3IO('/Volumes/Users/ht/Desktop/sbx/uni-day1_100_003')
# print q.path
# print repr(q.sbxpath.size)
# q.mat.show()
# q = Scanbox3IO('/Volumes/Users/ht/Desktop/sbx/uni-Day7_010_007')
# print q.path
# print repr(q.sbxpath.size)
# q.mat.show()

# q = Scanbox3IO('/Volumes/Users/ht/Desktop/sbx/Day0_000_007') # bi actually
# print q.path
# print repr(q.sbxpath.size)
# print 'framerate', (q.mat.resfreq / q.mat.recordsPerBuffer) * (1 if q.mat.scanmode else 2)
# q.mat.show()
# 
# q = Scanbox3IO('tmp/Jack/jzg1/day1/day3_022_000') # bi actually
# print q.path
# print repr(q.sbxpath.size)
# print 'framerate', (q.mat.resfreq / q.mat.recordsPerBuffer) * (1 if q.mat.scanmode else 2)
# q.mat.show()

# q = Scanbox3IO('/Volumes/Gandhi Lab - HT/sbx/my4r_1_3_000_011.mat') # dont know
# print q.path
# print repr(q.sbxpath.size)
# print 'framerate', (q.mat.resfreq / q.mat.recordsPerBuffer) * (1 if q.mat.scanmode else 2)
# q.mat.show()



# if q.mat.channels == 1:
#     nchan = 2;      # both PMT0 & 1
#     factor = 1;
# if q.mat.channels == 2:
#     nchan = 1;      # PMT 0
#     factor = 2;
# if q.mat.channels == 3:
#     nchan = 1;      # PMT 1
#     factor = 2;
# # because it is bidirectional, scanmode is 0
# if q.mat.scanmode == 0:
#     print 'it is bidirectional'
#     q.mat.recordsPerBuffer = q.mat.recordsPerBuffer * 2
#     q.mat.sz = [1024, 782]
# else:
#     print 'it is unidirectional'

# max_idx = int(q.sbxpath.size/q.mat.recordsPerBuffer/q.mat.sz[1]*factor/4 - 1)
# nsamples = (q.mat.sz[1] * q.mat.recordsPerBuffer * 2 * nchan) # size of each frame
# shape = nchan, q.mat.sz[1], q.mat.recordsPerBuffer, max_idx+1
# raw = np.memmap(q.sbxpath.str, shape=shape,
#     dtype='uint16', mode='r', order='F'
# ).transpose(0, 3, 2, 1) # [0, ...]

# from matplotlib.pyplot import *
# get_ipython().magic('pylab')
# # USE BELOW SNIPPET
# if q.mat.channels == 1: #pmt 0 and 1
#     width = q.mat.sz[1]
#     height = int(q.mat.sz[0] / 2)
#     raw = np.memmap(q.sbxpath.str, dtype='uint16', mode='r', order='F')
#     c0 = raw[0::2].reshape(-1, height, width*2)
#     c1 = raw[1::2].reshape(-1, height, width*2)
# 
#     f = ~(c0[0])
#     shift = int((f[0] == 65535).sum()/2)
#     left = f[:, :width]
#     right = np.roll(f[:, width:], -shift+2)
#     print left.shape
#     print right.shape
#     imsave('f0.png', f)
#     imsave('f00.png', left)
#     imsave('f01.png', right)
# 
# if q.mat.channels == 2: #pmt 0 only
#     width = q.mat.sz[1]
#     height = int(q.mat.sz[0] / 2)
#     raw = np.memmap(q.sbxpath.str, dtype='uint16', mode='r', order='F')
#     chan = raw.reshape(-1, height, width*2)
# 
#     f = ~(chan[0])
#     shift = int((f[0] == 65535).sum()/2)
#     left = f[:, :width]
#     right = np.roll(f[:, width:], -shift+2)
#     print left.shape
#     print right.shape
#     imsave('f0.png', f)
#     imsave('f00.png', left)
#     imsave('f01.png', right)

# from tifffile import TiffWriter
# with TiffWriter('ffff.tiff', bigtiff=True) as tif:
#     for i, frame in enumerate(c0):
#         f = ~frame
#         shift = int((f[0] == 65535).sum()/2)
#         left = f[:, :782]
#         right = np.roll(f[:, 782:], -shift+2)
#         tif.save(left)
#         tif.save(right)
#         print i
# 
# with open('test.npy', 'w') as npy:
#     for i, frame in enumerate(c0):
#         f = ~frame
#         shift = int((f[0] == 65535).sum()/2)
#         left = f[:, :782]
#         right = np.roll(f[:, 782:], -shift+2)
#         npy.write(left.tostring())
#         npy.write(right.tostring())
#         print i

# r = np.memmap('test.npy', dtype='uint16', mode='r', shape=(1066, 512, 782))
