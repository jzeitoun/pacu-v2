# import ctypes
# from multiprocessing import Array
# from multiprocessing import Process
# 
# import numpy as np
# 
# from pacu.util.path import Path
# # from pacu.core.scanbox import FileGroup
# from pacu.core.io.scanbox.impl import ScanboxIO
# 
# # binpath = '/Volumes/Users/ht/tmp/pysbx-data/JZ5/JZ5_000_003'
# # binpath = '/Volumes/Users/ht/tmp/pysbx-data/JZ7/9-21-15_000_007'
# # s = FileGroup(binpath)
# # raw = s.mat.memmap[..., 0]
# 
# #             self.raw = mmap[..., 0]
# #             # print 'invmin', 65535 - self.raw.max()
# #             # print 'invmax', 65535 - self.raw.min()
# #             self.mmap8 = self.raw.view('uint8')[..., 1::2]
# 
# # data = np.memmap(binpath, dtype=np.int32, mode='r', shape=shape)
# # binpath = Path.here('npbin')
# # shape = (800, 512, 512)
# # qwe = np.arange(reduce(int.__mul__, shape), dtype=np.int32).reshape(shape)
# # qwe.tofile(binpath.str)
# 
# import time
# 
# def mean(arr_in, arr_out, addr_in, addr_out):
#     # arr_out[:] = (~arr_in).mean(axis=(1,2))
#     if arr_in.ctypes.data != addr_in or arr_out.ctypes.data != addr_out:
#         print 'warning, memory copy was made...'
#     arr_out[:] = 65536.0 - arr_in.mean(axis=(1,2))
# 
# def get(self, x1, x2, y1, y2, src=''):
#     # turn off gzip encoding by setting "application" mime-type
#     # data = np.memmap(binpath, dtype=np.int32, mode='r', shape=shape)
# 
#     sbx = ScanboxIO(src)
#     # raw = s.p[..., 0]
#     # raw = s.mat.memmap[..., 0]
# 
#     x1, x2, y1, y2 = map(int, [x1, x2, y1, y2])
#     data = sbx[:, y1:y2, x1:x2]
#     result = np.ctypeslib.as_array(Array(ctypes.c_float, len(data)).get_obj())
#     ins, outs = [np.array_split(arr, 8) for arr in (data, result)]
# 
#     self.set_header('Content-Type', 'application/octet-stream; charset="us-ascii"')
#     self.set_header('Content-Length', result.nbytes)
# 
#     ps = [Process(target=mean, args=(arr_in, arr_out,
#         arr_in.ctypes.data, arr_out.ctypes.data))
#         for arr_in, arr_out in zip(ins, outs)]
#     for p in ps:
#         p.start()
#     for p, out in zip(ps, outs):
#         p.join()
#         self.write(out.tostring())
#         self.flush() # gives onprogress event
# 
# 
# 
# 
# 
