import itertools

from ..compat import PY3

zip = zip if PY3 else itertools.izip
map = map if PY3 else itertools.imap
filter = filter if PY3 else itertools.ifilter

def first_nonzero(*args):
    if len(args) == 1:
        it = args[0]
    else:
        it = map(*args)
    return next(filter(None, it), None)
