from ..path import Path

ORIGINAL_NAME = 'python-util-dinerk'
maybe_root = Path.here().parent.parent.resolve()
STANDALONE = maybe_root.name == ORIGINAL_NAME
SUBMODULE = not STANDALONE

from . import path
from . import log

name = path.name

def formattempfile(fmt):
    import os
    import tempfile
    return os.path.join(tempfile.gettempdir(), fmt % name)
