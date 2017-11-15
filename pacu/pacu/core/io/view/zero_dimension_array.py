from collections import namedtuple

import numpy as np
from scipy import io

reserved = {'_keys', '_vals', '_zip', 'show', 'from_mat'}
reserved_attr_error = Exception(
    'Some of fields used reserved keywords. ({})'.format(', '.join(reserved))
)

def is_zda(target): # zda zero dimension array
    return isinstance(target, np.ndarray) and target.shape == ()

class ZeroDimensionArrayView(object):
    """
    mat_file = '/Volumes/Users/ht/Desktop/sbx/uni-Day0_000_007.mat'
    zdav = ZeroDimensionArrayView.from_mat(mat_file)
    """
    @property
    def _zip(self): # fail-safe and easy
        return [(k, getattr(self, k, v)) for k, v in zip(self._keys, self._vals)]
    def __init__(self, array):
        self._keys = array.dtype.names
        self._vals = array.item()
        self._dict = dict(zip(self._keys, self._vals))
        if reserved & set(self._keys):
            raise reserved_attr_error
        # self._namedtuple = namedtuple('Contents', self._names)._make(
        #     ZeroDimensionArrayView(item) if is_zda(item) else item
        #     for item in self._items
        # )
        self.__dict__.update({
            key: ZeroDimensionArrayView(val) if is_zda(val) else val
            for key, val in self._zip})
    def __repr__(self):
        kvs = ', '.join(['{}={!s}'.format(k, v) for k, v in self._zip])
        return '{}({})'.format(type(self).__name__, kvs)
    def __iter__(self):
        return iter(self._zip)
    def show(self, level=0):
        if level == 0:
            print '-' * 80
        for k, v in self._zip:
            if isinstance(v, ZeroDimensionArrayView):
                print '-' * 80
                print ('\t' * level) + k
                v.show(level+1)
            else:
                print ('\t' * level) + '{}: {}'.format(k, v)
        if level == 0:
            print '-' * 80
    @classmethod
    def from_mat(cls, path, **kwargs):
        return cls(io.loadmat(path, squeeze_me=True, **kwargs).get('info'))

#     def __dir__(self):
#         return list(self._names) + list(reserved)
#     def __getattr__(self, attr):
#         return getattr(self._namedtuple, attr)
#     def __iter__(self):
#         return iter(
#             (key, list(val) if isinstance(val, ZeroDimensionArrayView) else str(val))
#             for key, val in self._namedtuple._asdict().items()
#         )
    def items(self):
        return {
            key: (val.items() if isinstance(val, ZeroDimensionArrayView) else str(val))
            for key, val in list(self)
        }
