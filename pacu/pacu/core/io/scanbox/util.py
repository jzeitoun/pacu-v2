# testpath = Path('/Volumes/Data/Recordings/scanbox-jack/Dario/test')
# def conv(path, nchan=2):
#     sbx = ScanboxIO(path)
#     x, y, _, z = sbx.shape
#     rgb = np.zeros((z, y, x, 3), dtype=sbx.io.dtype)
#     if nchan == 2:
#         rgb[..., 1] = ~sbx.ch0
#         rgb[..., 0] = ~sbx.ch1
#     elif nchan == 1:
#         rgb[..., 1] = ~sbx.ch0
#     tiffpath = sbx.path.with_name('tiff').mkdir_if_none()
#     dest = tiffpath.joinpath(sbx.path.name).with_suffix('.tiff')
#     tifffile.imsave(dest.str, rgb)
# def conv_all(path, nchan=2, ls='*.sbx'):
#     for sbxpath in Path(path).ls(ls):
#         print 'converting...', sbxpath
#         conv(sbxpath, nchan=nchan)
# 
# # testpath = Path('/Volumes/Data/Recordings/scanbox-jack/Dario/test2/test2_000_002')
# 
# def combine(tiffpath, dest, ls='*.tiff'):
#     path = Path(tiffpath)
#     # movie = np.concatenate([
#     #     tifffile.imread(filename.str).mean(axis=0)[np.newaxis, ...]
#     #     for filename in path.ls(ls)
#     # ])
#     movie = np.stack(
#         tifffile.imread(filename.str).mean(axis=0)
#         for filename in path.ls(ls)
#     )
#     tifffile.imsave(path.joinpath(dest).with_suffix('.tiff').str, movie)
#     # consider using just stack instead of concatenate
# 
# def conv_comb(path, lspath='*', nchan=2):
#     """
#     path = '/media/Data/Recordings/scanbox-jack/Dario/Convert Please/Tox 3 D3'
#     ls = 'D3_000_*'
#     nchan = 2
#     """
#     path = Path(path)
#     lspath = Path(lspath)
#     print 'path', path
#     print 'for', lspath
#     tiffpath = path.joinpath('tiff')
#     print 'conv all first'
#     conv_all(path, nchan=nchan, ls=lspath.with_suffix('.sbx').str)
#     print 'combine...'
#     combine(tiffpath, '{}.mean.tiff'.format(lspath.str.replace('*', '')), ls=lspath.stem)


# from pacu.core.io.scanbox import impl as sbx

# testpath = Path('/Volumes/Users/ht/Desktop/test2/test2_000_001')
# s1 = ScanboxIO(testpath)
# testpath = Path('/Volumes/Users/ht/Desktop/test2/test2_000_002')
# s2 = ScanboxIO(testpath)
# get_ipython().magic('pylab')

# testpath = Path('/Volumes/Data/Recordings/scanbox-jack/Dario/tox3')
# conv_all(testpath, nchan=2, ls='Tox3_000_*.sbx')

# from pacu.util.path import Path
# from pacu.util.path import Path
#
#
# from pacu.core.io.scanbox import impl as sbx
# sbx.conv_all('/media/Data/Recordings/scanbox-jack/Dario/Tox3', nchan=2, ls='Tox3_000_*')
# sbx.conv_all('/media/Data/Recordings/scanbox-jack/Dario/Tox3', nchan=2, ls='Tox3_001_*')
# get_ipython().magic(u'ed ')
# combine('/media/Data/Recordings/scanbox-jack/Dario/Tox3/tiff', nchan='001.mean.tiff', ls='Tox3_001_*')
# combine('/media/Data/Recordings/scanbox-jack/Dario/Tox3/tiff', '001.mean.tiff', ls='Tox3_001_*')
# get_ipython().magic(u'ed -p')
# combine('/media/Data/Recordings/scanbox-jack/Dario/Tox3/tiff', '001.mean.tiff', ls='Tox3_001_*')
# get_ipython().magic(u'ed -p')
# combine('/media/Data/Recordings/scanbox-jack/Dario/Tox3/tiff', '001.mean.tiff', ls='Tox3_001_*')
# get_ipython().magic(u'ed -p')
# combine('/media/Data/Recordings/scanbox-jack/Dario/Tox3/tiff', '001.mean.tiff', ls='Tox3_001_*')
# combine('/media/Data/Recordings/scanbox-jack/Dario/Tox3/tiff', '000.mean.tiff', ls='Tox3_000_*')
# get_ipython().magic(u'ed 0-14')
