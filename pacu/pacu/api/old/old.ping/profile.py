from __future__ import absolute_import

from collections import OrderedDict

from pacu.util import identity

def ping():
    return OrderedDict([
        ('local-recording-root', identity.path.cwd),
    ])
