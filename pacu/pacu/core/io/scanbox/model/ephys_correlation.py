import base64
import time

import matplotlib
#matplotlib.use('svg')
from matplotlib import pyplot
import numpy as np
from cStringIO import StringIO
from zipfile import ZipFile, ZIP_DEFLATED

from sqlalchemy import Column, UnicodeText, Integer
from sqlalchemy.types import PickleType

from pacu.core.io.scanbox.model.base import SQLite3Base

class EphysCorrelation(SQLite3Base):
    __tablename__ = 'ephys_correlations'
    traces = Column(PickleType, default=[])
    meantrace = Column(PickleType, default=[])
    rmeantrace = Column(PickleType, default=[])
    rstdtrace = Column(PickleType, default=[])
    roi_ids = Column(PickleType, default=[])
    window = Column(Integer, default=100)
    random_count = Column(Integer, default=100)
    note = Column(UnicodeText)
    def refresh(self):
        # incremental table altering could not assign a default value at appended column.
        self.random_count = self.random_count or 100
        ws = self.workspace
        window = self.window
        before = 100
        rois = [roi for roi in ws.rois if roi.id in self.roi_ids]
        arrays = [r.traces[0].array for r in rois]
        peaks = np.flatnonzero(np.array(ws.io.ephys.trace))
        slices = [slice(s, e) for s, e in zip(peaks-window, peaks+window)
            if 0 <= s]
        traces = [array[sl] for array in arrays for sl in slices]
        if not traces:
            raise Exception('There is no ephys trace bound.')
        maxlen = max(map(len, traces))
        traces = np.array([t for t in traces if len(t) == maxlen])
        bases = traces[:, window-before:window].mean(1)
        traces = np.array([(trace-base)/base
            for trace, base in zip(traces, bases)])
        meantrace = traces.mean(0)

        def randomize(iteration=0):
            rands = np.random.choice(
                np.arange(len(ws.io.ephys.trace)),len(peaks), replace=False)
            rslices = [slice(s, e) for s, e in zip(rands-window, rands+window)
                if 0 <= s]
            rtraces = [array[sl] for array in arrays for sl in rslices]
            rmaxlen = max(map(len, rtraces))
            rtraces = np.array([t for t in rtraces if len(t) == rmaxlen])
            rbases = rtraces[:, window-before:window].mean(1)
            rtraces = np.array([(t-b)/b
                for t, b in zip(rtraces, rbases)])
            rmeantrace = rtraces.mean(0)
            return rmeantrace

        rands = np.vstack([randomize(i) for i in range(self.random_count)])
        self.rstdtrace = rands.std(0)
        self.rmeantrace = rands.mean(0)
        self.meantrace = meantrace
        self.traces = traces
        return self
    def export_zip(self):
        io = StringIO()
        with ZipFile(io, 'w', compression=ZIP_DEFLATED) as z:
            z.writestr('raw.csv', self.to_csv())
            z.writestr('raster.png', self.to_png())
            z.writestr('vector.pdf', self.to_pdf())
        return io.getvalue()
    def export_zip_to_local(self, filename='temp.zip'):
        with open(filename, 'wb') as f:
            f.write(self.export_zip())
    def export_zip_for_download(self):
        return dict(
            filename='{}-ephys-{}-with-rois-{}.zip'.format(
                time.time(), self.id, '_'.join(map(str, self.roi_ids))),
            mimetype='application/zip',
            encoded='base64',
            data=base64.b64encode(self.export_zip()),
        )
    def to_csv(self):
        io = StringIO()
        arr = np.rec.array([self.meantrace, self.rmeantrace, self.rstdtrace],
            names=[
                'MEASURE_MEAN',
                'RANDOM({0})_MEAN'.format(self.random_count),
                'RANDOM({0})_STD'.format(self.random_count),
            ])
        io.write(','.join(arr.dtype.names))
        io.write('\n')
        np.savetxt(io, arr, fmt='%s', delimiter=',')
        return io.getvalue()
    def to_png(self):
        x = (np.arange(self.window*2) - self.window) / 30.0
        raster = StringIO()
        fig = pyplot.figure()
        plt = fig.add_subplot(111)
        plt.plot(x, self.meantrace, label='measure')
        plt.errorbar(x, self.rmeantrace,
            label='random({})'.format(self.random_count),
            yerr=self.rstdtrace,
            elinewidth=0.25,
            capthick=0.25)
        plt.legend()
        fig.savefig(raster, format='png', dpi=300, bbox_inches='tight')
        return raster.getvalue()
    def to_pdf(self):
        x = (np.arange(self.window*2) - self.window) / 30.0
        vector = StringIO()
        fig = pyplot.figure()
        plt = fig.add_subplot(111)
        plt.plot(x, self.meantrace, label='measure')
        plt.errorbar(x, self.rmeantrace,
            label='random({})'.format(self.random_count),
            yerr=self.rstdtrace,
            elinewidth=0.25,
            capthick=0.25)
        plt.legend()
        fig.savefig(vector, format='pdf', bbox_inches='tight')
        return vector.getvalue()
