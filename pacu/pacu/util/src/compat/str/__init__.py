from .. import PY2

if PY2:
    from .str2 import str
else:
    from .str3 import str
