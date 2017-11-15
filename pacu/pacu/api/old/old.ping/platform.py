from __future__ import absolute_import

import platform
from collections import OrderedDict

def ping():
    keys = 'system node release version machine processor'.split()
    vals = platform.uname()
    odict = OrderedDict(zip(keys, vals))
    del odict['version']
    return odict
