import numpy.core.memmap as memmap
import matplotlib.pyplot as plt

# scanbox data should take complementary number (inverse)
class Stack(object):
    mmap = None
    error = None
    def __init__(self, mmap):
        if isinstance(mmap, memmap):
            self.raw = mmap[..., 0]
            # print 'invmin', 65535 - self.raw.max()
            # print 'invmax', 65535 - self.raw.min()
            self.mmap8 = self.raw.view('uint8')[..., 1::2]
            self.cm = getattr(plt.cm, 'jet')
            self.shape = self.raw.shape
        else:
            self.error = TypeError(mmap)
    def get_frame(self, index=0): # returns binary
        return self.cm(~self.mmap8[index], bytes=True).tostring()
        # return self.cm(~self.mmap[index], bytes=True).tostring()
    # getbuffer

# In [5]: qwe.stack.raw.min()
# Out[5]: memmap(811, dtype=uint16)
# 
# In [6]: qwe.stack.raw.max()
# Out[6]: memmap(64148, dtype=uint16)
# 
# In [7]: cm
