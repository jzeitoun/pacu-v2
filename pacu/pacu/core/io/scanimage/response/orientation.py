import numpy as np

from pacu.core.io.scanimage.trace.whole import WholeTrace

class Orientation(object):
    capture_frequency = 6.1 # default
    def __init__(self, value, ontimes, offtimes, baselines):
        self.value = value
        self.ontimes = ontimes
        self.offtimes = offtimes
        self.baselines = baselines
    @classmethod
    def from_adaptor(cls, value, trace, adt):
        trace = WholeTrace(trace.copy())
        ontimes = trace.zip_slice(adt.indice.ontimes)
        baselines = trace.zip_slice(adt.indice.baselines)
        offtimes = trace.zip_slice(adt.indice.offtimes)
        nframes_on = int(round(adt.rec.duration_F))
        nframes_off = int(round(adt.rec.waitinterval_F))
        for ontime, baseline in zip(ontimes, baselines):
            ontime.compensate(baseline, adt.frame.baseline)

        print 'Verifying recording duration of orientation {}'.format(value)
        for index, ontime in enumerate(ontimes):
            length_on = len(ontime.array)
            if nframes_on != length_on:
                ontime.array = np.concatenate([ontime.array,
                    np.full(nframes_on-length_on, np.nan)])
                print ('Trial #{} has ontime duration mismatch ({}/{}), '
                       'fixed with NaNs').format(index, length_on, nframes_on)
        for index, offtime in enumerate(offtimes):
            length_off = len(offtime.array)
            if nframes_off != length_off:
                offtime.array = np.concatenate([offtime.array,
                    np.full(nframes_off-length_off, np.nan)])
                print ('Trial #{} has offtime duration mismatch ({}/{}), '
                       'fixed with NaNs').format(index, length_off, nframes_off)

        self = cls(value, ontimes, offtimes, baselines)
        self.capture_frequency = adt.capture_frequency
        self.nframes_on = nframes_on
        self.nframes_off = nframes_off

        # print 'len base', [len(t.array) for t in baselines]
        return self
    def __repr__(self):
        return '{}({})'.format(type(self).__name__, self.value)
    @property
    def mean(self):
        return self.meantrace.mean()
    @property
    def meantrace(self):
        return np.array([rep.array for rep in self.ontimes]).mean(0)
    @property
    def windowed_mean_for_ontimes(self):
        """
        Dario mentioned 2016-09-19 UTC+9:
        Maybe default it to use all frames for meantrace and 1/4 of the baseline.
        """
        return [trial.array[
            # int(1*self.capture_frequency):int(2*self.capture_frequency)
            :
        ].mean() for trial in self.ontimes]
    @property
    def regular_mean_for_ontimes(self):
        return [trial.array[:].mean() for trial in self.ontimes]
    def toDict(self):
        return vars(self)
