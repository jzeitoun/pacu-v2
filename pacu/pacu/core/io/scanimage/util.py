import numpy as np

def infer_nchannels(tiff):
    try:
        print 'Number of channel is 2, fixed, no inferring.'
        return 2
        print 'Dario is inferring how many channels there are...'
        maybe1 = tiff[0:100:2]
        maybe1_range = maybe1.max() - maybe1.min()
        maybe2 = tiff[1:101:2]
        maybe2_range = maybe2.max() - maybe2.min()
        if maybe1_range < 2*maybe2_range:
            nchan = 2
        else:
            nchan = 1
        # print '`mean` of [0::2]', maybe1
        # print '`mean` of [1::2]', maybe2
        # nchan = 2 if  maybe1 / maybe2 < 0.75 else 1
        print 'Now Dario knows this stack has {} channel(s).'.format(nchan)
    except Exception as e:
        print 'Can not determine the number of channels.'
        print e
        return 0
    else:
        return nchan

def nan_for_list(iterable):
    return ['nan' if isinstance(e, float) and np.isnan(e) else e for e in iterable]
def nan_for_json(dt):
    new = {}
    for key, val in dt.items():
        if isinstance(val, np.ndarray):
            new[key] = val
        elif isinstance(val, str):
            new[key] = val
        elif isinstance(val, dict):
            new[key] = nan_for_json(val)
        elif hasattr(val, '__iter__'):
            new[key] = val
        elif val is None:
            new[key] = ''
        elif np.isinf(val):
            new[key] = 'inf'
        elif np.isnan(val):
            new[key] = 'nan'
        else:
            new[key] = val
    return new
