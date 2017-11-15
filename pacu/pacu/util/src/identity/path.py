import os

from ..identity import Path
from ..identity import maybe_root
from ..identity import STANDALONE

src = maybe_root.joinpath('src') if STANDALONE else maybe_root.parent
root = src.parent
doc = src // 'doc'
test = src // 'test'
ember = src.joinpath('ember', 'dist')
name = src.parent.name
userenv = Path(os.path.expanduser('~/.%s' % name))
cwd = Path(os.getcwd())
