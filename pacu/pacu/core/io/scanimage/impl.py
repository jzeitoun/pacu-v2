from __future__ import division

import shutil
from scipy import io
from cStringIO import StringIO

import tifffile
import numpy as np

from pacu.profile import manager
from pacu.util.path import Path
from pacu.util.misc.unit.size import SizeUnit
from pacu.util.prop.memoized import memoized_property
from pacu.core.io.scanimage.channel import ScanimageChannel
from pacu.core.io.scanimage.session import ScanimageSession
from pacu.core.io.scanimage.adaptor.db import ScanimageDBAdaptor
from pacu.core.io.scanimage import util
from pacu.core.io.scanimage.roi.impl import ROI
from pacu.core.io.scanimage.response.impl import Response
from pacu.core.io.scanimage.response.main import MainResponse
from pacu.core.io.scanimage.response.roi import ROIResponse
from pacu.core.io.scanimage.response.orientation import Orientation
from pacu.core.io.scanimage.response.bootstrap import BootstrapResponse

def validate_guess_params(params):
    validated = {}
    try:
        for sf, param in params.items():
            (p1, p2), (p3, p4), (p5, p6), (p7, p8) = param
            validated[float(sf)] = (
                (float(p1), float(p2)),
                (float(p3), float(p4)),
                (float(p5), float(p6)),
                (float(p7), float(p8)),
            )
    except Exception as e:
        raise Exception(
            'Can not initialize initial guess. Did you set correct numbers?')
    return validated
class ScanimageIO(object):
    session_name = 'main'
    r_value = 0.7
    def __init__(self, path):
        # wself.path = Path(str(path) + '.imported')
        if '.imported' in str(path):
            self.path = Path(path)
        else:
            self.path = Path(str(path) + '.imported')
    @classmethod
    def get_record(cls, rec_path):
        return ScanimageRecord(rec_path)
    @property
    def exists(self):
        return self.path.is_dir()
    @memoized_property
    def tiff(self):
        tiffpath = self.path.with_suffix('.tif')
        print 'Import from {}...Please allow a few minutes.'.format(tiffpath.name)
        return tifffile.imread(tiffpath.str)
    def import_raw(self):
        if self.exists:
            return False
        nchan = util.infer_nchannels(self.tiff)
        if nchan:
            self.create_package_path()
            self.convert_channels(nchan)
        else:
            print 'Unable to import data.'
        print 'Import done!'
        return self.toDict()
    def create_package_path(self):
        self.path.mkdir()
        print 'Path `{}` created.'.format(self.path.str)
    def remove_package(self):
        shutil.rmtree(self.path.str)
        return self.toDict()
    def convert_channels(self, nchan):
        for index in range(nchan):
            self.convert_channel(nchan, index)
    def convert_channel(self, nchan, chan):
        tiff = self.tiff[chan::nchan]
        print 'Converting channel {}...({} frames.)'.format(chan, len(tiff))
        return getattr(self, 'ch{}'.format(chan)).import_raw(tiff)
    def toDict(self):
        return dict(exists=self.exists, path=self.path.str, sessions=self.sessions)
    @memoized_property
    def ch0(self):
        return ScanimageChannel(self.path.joinpath('ch0'))
    @memoized_property
    def ch1(self):
        return ScanimageChannel(self.path.joinpath('ch1'))
    @memoized_property
    def channel(self):
        chan = self.session.opt.setdefault('channel', 0)
        return getattr(self, 'ch{}'.format(chan))
    @channel.invalidator
    def set_channel(self, channel):
        self.session.opt['channel'] = channel
        return self
    @property
    def nchannel(self):
        return len(list(self.path.glob('ch?.mmap.npy')))
    @property
    def channel_numbers(self):
        return list(range(self.nchannel))
    @property
    def channel_number(self):
        return self.session.opt['channel']
    colormap_index = 0
    colormaps = ['jet', 'gray', 'gist_heat', 'afmhot', 'bone']
    @property
    def has_blank_and_flicker(self):
        if self.db:
            rec = self.db.rec
            return [rec.blankOn, rec.flickerOn]
        else:
            return [None, None]
    @property
    def sfrequency(self):
        return self.db.locator.sfrequencies.current if self.db else ''
        # return self.session.opt.setdefault(#  'sfrequency', )
    @property
    def sfrequency_index(self):
        return self.sfrequencies.index(self.sfrequency) if self.sfrequency else 0
    @property
    def sfrequencies(self):
        return self.db.locator.sfrequencies if self.db else []
    @property
    def orientations(self):
        return self.db.orientations if self.db else []
    # @sfrequency.invalidator
    def set_sfrequency_index(self, sfreq_index):
        self.sfrequencies.set_cursor(sfreq_index)
        self.session.opt['sfrequency'] = self.sfrequencies.current
        self.session.opt.save()
        return dict(index=sfreq_index, value=self.sfrequency)
    @memoized_property
    def db(self):
        return ScanimageDBAdaptor(self.session.ed) if self.session.ed else None
    @property
    def main_response(self):
        return MainResponse.from_adaptor(self.channel.stat.MEAN, self.db)
    @property
    def sessions(self):
        return map(ScanimageSession, sorted(self.path.ls('*.session')))
    @memoized_property
    def session(self):
        return ScanimageSession(
            self.path.joinpath(self.session_name).with_suffix('.session'))
    @session.invalidator
    def set_session(self, session_name):
        self.session_name = session_name
        return self
    def upsert_roi(self, roi_kwargs):
        gp = validate_guess_params(roi_kwargs.pop('guessParams', {}))
        return self.session.roi.upsert(ROI(guess_params=gp, **roi_kwargs))
    def invalidate_rois(self):
        for roi in self.session.roi.values():
            roi.invalidated = True
            roi.blank = None
            roi.flicker = None
            roi.responses = {}
    def export_sfreqfit_data_as_mat(self, rid):
        roi = self.session.roi[rid]
        sio = StringIO()
        value = roi.sfreqfit.toDict()
        io.savemat(sio, value)
        return sio.getvalue()
    def update_responses(self, id, heavy=False):
        roi = self.session.roi[id]
        trace = self.make_trace(roi)
        if self.session.ed:
            with self.session.roi.bulk_on:
                try:
                    if self.db.locator.override_blank(True):
                        roi.blank = Orientation.from_adaptor('blank', trace, self.db)
                    if self.db.locator.override_flicker(True):
                        roi.flicker = Orientation.from_adaptor('flicker', trace, self.db)
                finally:
                    self.db.locator.override()
                for sf in self.db.locator.sfrequencies.loop():
                    response = ROIResponse.from_adaptor(roi, trace, self.db)
                    roi.responses[self.sfrequency] = response
                roi.update_with_adaptor(self.db)
                for sf, resp in roi.sorted_responses:
                    gp = roi.guess_params.get(sf) or resp.sog_initial_guess
                    print 'SoG custom guess for {}: {}'.format(sf, gp)
                    resp.update_fit_and_decay(roi, self.db, gp, heavy)
                p_value = roi.anova_all.get('p')
                if heavy:
                    if p_value < 0.01:
                        print ('Computing bootstrap for preferred SF')
                        #     '{} conditions...').format(
                        #     len(self.db.orientations) * len(self.db.sfrequencies))
                        roi.update_bootstrap_for_sf(self.db)
                        peaksf = roi.sfreqfit.peak_sfreq.x
                        peak_resp = roi.responses[peaksf]
                        print 'Determine peak spatial frequency: {}'.format(peaksf)
                        peak_resp.bootstrap = BootstrapResponse.from_adaptor(
                                peak_resp, self.db)
                    else:
                        print ('P value is not less than 0.01. ({}) '
                               'Skip bootstrap.').format(p_value)

                roi.invalidated = False
                print 'Done updating response for ROI ' + str(roi.id)
                print ' '
                print ' '
                return self.session.roi.upsert(roi)
        else:
            response = ROIResponse.from_scanbox(roi, trace)
            roi.responses[self.sfrequency] = response
            roi.update_with_adaptor(self.db)
            roi.invalidated = False
            return self.session.roi.upsert(roi)
    sog_initial_guess = ((0, 1), (0, 1), (15, 60), (0, 0.01))
    def make_delta_trace(self, roi, trace, dx=0, dy=0):
        extras = self.session.roi.values()
        extras.remove(roi)
        main_trace, main_mask = roi.trace(trace, dx, dy)
        neur_trace, neur_mask = roi.neuropil_trace(trace, extras, dx, dy)
        return main_trace - neur_trace*self.r_value
    def make_trace(self, roi, old=False): # checked same function
        if old:
            # print 'no centroid yet...perform old'
            extras = self.session.roi.values()
            extras.remove(roi)
            main_trace, main_mask = roi.trace(self.channel.mmap)
            neur_trace, neur_mask = roi.neuropil_trace(self.channel.mmap, extras)
            # neuropil_mask, roi_mask = roi.trim_bounding_mask(neur_mask, main_mask)
            # roi.masks = dict(
            #     neuripil = neuropil_mask.tolist(),
            #     roi = roi_mask.tolist())
            return main_trace - neur_trace*self.r_value
        else:
            # print 'has centroid...perform new'
            vecs = roi.split_by_vectors(len(self.channel.mmap))
            traces = np.split(self.channel.mmap, vecs.index[1:])
            return np.concatenate([
                self.make_delta_trace(roi, trace, dx, dy)
                for dx, dy, trace in zip(vecs.x, vecs.y, traces)])
    def export_plots(self, id):
        roi = self.session.roi[id]
        return roi.export_plots_as_zip_for_download()

# import pandas as pd
# from pacu.core.io.scanimage.response.orientation import Orientation

# path = 'tmp/Dario/2016.12.05/r.160722.10/Contra_001'
# qwe = ScanimageIO(path).set_session('xiao')
# asd = qwe.session.roi.values()[0]

# path = 'tmp/Dario/2015.04.18/x.150322.1/Contra_001'
# qwe = ScanimageIO(path).set_session('ht')
# asd = qwe.session.roi.values()[0]


# from scipy import stats

# import matplotlib
# import matplotlib.pyplot as plt
# plt.ioff()
# path = 'tmp/Dario/2016.01.27/r.151117.3/DM9_RbV1_Contra004004'

# import ujson
# path = 'tmp/Dario/2014.06.13/x.140513.3/field2001'

# path = 'tmp/Dario/2016.05.06/r.160309.1/DM24_RbV1_Contra_005'
# qwe = ScanimageIO(path).set_session('main')
# r = qwe.session.roi.items()[0][1]

# r = qwe.session.roi.values()[0]
# r = qwe.session.roi['1477437377.839845']

# asd = qwe.session.roi.values()
# q = qwe.session.roi['1464301377.401976']
# for index, roi in enumerate(asd):
# #     roi.sfreqfit.plot_local('{}.pdf'.format(index))
#     try:
#         d = ujson.dumps(roi)
# #         ujson.loads(d)
#     except Exception as e:
#         eroi = roi
#         print e, index
#         break
# #         errs.append(roi)
# 
# for r in asd:
#     a =r.toDict()
# for key, roi in qwe.session.roi.items():
#     roi.sfreqfit.plot_local()
# asd = qwe.session.roi.one().val
# asd.sfreqfit.plot_local('sf4p.png')
# svgdata = asd.sfreqfit.plot_io(False)
# with open('fig.svg', 'w') as f:
#    f.write(svgdata)


# roi = qwe.session.roi.one().val

# r.orientations.plot()
# r.normalfit.plot()
# r.decay.plot()

# import matplotlib
# matplotlib.use('svg')

# if __name__ == '__main__':
#     get_ipython().magic('pylab')



# badpath = Path('tmp/Dario/2016.04.19/x.160103.1/DM15_RbV1_Contra_2.1')
# qwe = ScanimageIO(badpath)
# r = roi.responses.get(0.05)

# 
# for sf, r in roi.sorted_responses:
#     print
#     print 'Spatial Frequency', sf
#     print '\told anova:', r.anova
#     print '\tnew anova:', r.anova2

# print r.normalfit.measure
# print r.orientations.windowed_ontimes.mean(1)
# print r.orientations.windowed_ontimes.shape
# print r.orientations.ons.mean(axis=(2))

# asd = r.orientations.ons[ # aka meanresponses
#     ...,
#     int(1*6.1):int(2*6.1)
# ] #.mean(axis=(1, 2))
# print asd.mean(axis=(1, 2))

# b_reps = [ont.array.mean() for ont in r.blank.ontimes]
# f_reps = [ont.array.mean() for ont in r.flicker.ontimes]
# oris = [
#     [ont.array.mean() for ont in ori.ontimes]
#     for ori in r.orientations.responses]
# flat = b_reps + f_reps + [p for ori in oris for p in ori]
# f, p = stats.f_oneway(b_reps, f_reps, *oris)
# print 'f', f, 'p', p
# 
class ScanimageRecord(object):
    """
    For `compatible_path`,
    the path should be formed like below. For example,
    '/Volumes/Data/Recordings/2P1/Dario/2015.11.20/x.151101.4/ref_p19_005.tif',
    This will be considered as,
    {whatever_basepath}/{experimenter}/{date}/{mousename}/{imagename}
    So the directory structure always will matter.
    """
    def __init__(self, compatible_path):
        self.tiff_path = Path(compatible_path).with_suffix('.tif')
        self.package_path = Path(compatible_path).with_suffix('.imported')
        self.mouse, self.date, self.user = self.tiff_path.parts[::-1][1:4]
    def toDict(self):
        return dict(
            user = self.user,
            mouse = self.mouse,
            date = self.date,
            desc = self.desc,
            name = self.tiff_path.stem,
            package = self.package
       )
    @memoized_property
    def package(self):
        return ScanimageIO(self.package_path)
    @property
    def desc(self):
        return '{}'.format(
            SizeUnit(self.tiff_path.stat().st_size)
            # tifffile.format_size(self.tiff_path.stat().st_size)
        )

def testdump():
    path = 'tmp/Dario/2015.12.02/x.151101.2/bV1_Contra_004'
    qwe = ScanimageIO(path)
    qwe.session.roi.clear()
    qwe.session.opt.clear()
    from pacu.util.identity import path
    rois = path.cwd.ls('*pickle')[0].load_pickle().get('rois')
    pgs = [[dict(x=x, y=y) for x, y in roi] for roi in rois]
    kws = [dict(polygon=p) for p in pgs]
    for kw in kws:
        qwe.session.roi.upsert(ROI(**kw))

def test():
    path = 'tmp/Dario/2016.01.27/r.151117.3/DM9_RbV1_Contra004004'
    qwe = ScanimageIO(path)
    qwe.session.roi.clear()
    qwe.session.opt.clear()
    rois = [
        ([75,27], [71,27], [69,30], [69,34], [71,36], [75,36], [78,35], [79,32], [78,29]),
        ([60,72], [57,72], [55,75], [56,78], [58,79], [62,79], [64,76], [63,73]),
        ([53,47], [51,44], [48,43], [45,43], [43,46], [43,49], [46,51], [50,51], [52,50]),
        ([53, 104], [55, 108], [59, 110], [64, 109], [65, 105], [63, 101], [58, 100], [55, 101])
    ]
    pgs = [[dict(x=x, y=y) for x, y in roi] for roi in rois]
    kws = [dict(polygon=p) for p in pgs]
    for kw in kws:
        roi = qwe.session.roi.upsert(ROI(**kw))
        # qwe.update_responses(roi.id)

def ScanimageIOFetcher(year, month, day, mouse, image, session):
    root = manager.instance('opt').scanimage_root
    date = '{}.{:2}.{:2}'.format(year, month, day)
    path = Path(root).joinpath(date, mouse, image)
    return ScanimageIO(path).set_session(session)
