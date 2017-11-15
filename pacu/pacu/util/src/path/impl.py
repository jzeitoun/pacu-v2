import os
import shutil
import inspect
from datetime import datetime
import cPickle as pickle

from ..compat.pathlib import Path
from ..misc.unit.size import SizeUnit

def ls(self, glob='*'):
    return list(self.glob(glob))
def lsmodule(self, glob='*'):
    return [path.parent for path in self.glob('%s/__init__.py' % glob)]
def has_file(self, filename):
    return (self / filename).is_file()
def read(self, mode='r'):
    with self.open(mode) as f:
        return f.read()
def load_pickle(self, mode='rb'):
    with self.open(mode) as f:
        return pickle.load(f)
def dump_pickle(self, obj, mode='wb'):
    with self.open(mode) as f:
        return pickle.dump(obj, f)
# load json
# dump json
def peak(self):
    try:
        return self.read()
    except:
        return ''
def write(self, content, mode='w'):
    with self.open(mode) as f:
        return f.write(content)
def here(cls, *paths):
    """
    Since it uses inspect module to access caller's frame,
    it should not be wrapped by any other functions.
    """
    cur = inspect.currentframe()
    out = inspect.getouterframes(cur)[1][0]
    path = os.path.dirname(os.path.abspath(
        inspect.getfile(out)
    ))
    return cls(path).joinpath(*paths)
def absdir(cls, path):
    return cls(os.path.dirname(os.path.abspath(path)))
def merge_suffix(self, suffix, on):
    suffixes = self.suffixes
    if suffix in suffixes:
        return self
    try:
        suffixes[suffixes.index(on)] = suffix
    except ValueError as e:
        raise ValueError(
            '{!r} is not in the suffixes. ({!r})'.format(on, suffixes))
    return self.with_name(self.stem_least).with_suffix(''.join(suffixes))
def merge_or_join_suffix(self, suffix, on):
    try:
        return self.merge_suffix(suffix, on=on)
    except ValueError:
        return self.join_suffixes(suffix)
def stem_least(self):
    return self.name[:-len(''.join(self.suffixes))]
def ensure_suffix(self, suffix):
    if self.suffix != suffix:
        raise ValueError(
            'Path `{}` failed to match {!r} == {!r}.'.format(
                self, self.suffix, suffix))
    return self
def with_suffixes(self, *suffixes):
    return map(self.with_suffix, suffixes)
def join_suffixes(self, *suffixes):
    for suffix in suffixes:
        drv, root, parts = self._flavour.parse_parts((suffix,))
        if drv or root or len(parts) != 1:
            raise ValueError("Invalid suffix %r" % (suffix))
        suffix = parts[0]
        if not suffix.startswith('.'):
            raise ValueError("Invalid suffix %r" % (suffix))
    return self.with_name(self.stem_least
            ).with_suffix(''.join(self.suffixes + list(suffixes)))
# def path_without_suffixes(self):
#     return Path(self.str[:-len(''.join(self.suffixes))])
def stempath(self):
    return Path(self.str[:-len(''.join(self.suffixes))])
    # return Path(self.stem)
def mkdir_if_none(self, mode=511, parents=True):
    if not self.is_dir():
        self.mkdir(mode=mode, parents=parents)
    return self
def created_at(self):
    return datetime.fromtimestamp(self.stat().st_ctime)
def size(self):
    return SizeUnit(self.stat().st_size)
def rmtree(self, ignore_errors=True, onerror=None):
    return shutil.rmtree(self.str,
        ignore_errors=ignore_errors, onerror=onerror)

Path.__floordiv__ = Path.with_name
Path.str = property(Path.__str__)
Path.ls = ls
Path.lsmodule = lsmodule
Path.has_file = has_file
Path.read = read
Path.load_pickle = load_pickle
Path.dump_pickle = dump_pickle
Path.peak = peak
Path.write = write
Path.here = classmethod(here)
Path.absdir = classmethod(absdir)
Path.with_suffixes = with_suffixes
Path.ensure_suffix = ensure_suffix
Path.merge_suffix = merge_suffix
Path.merge_or_join_suffix = merge_or_join_suffix
Path.join_suffixes = join_suffixes
Path.stem_least = property(stem_least)
# Path.path_without_suffixes = property(path_without_suffixes)
Path.created_at = property(created_at)
Path.size = property(size)
Path.stempath = property(stempath)
Path.mkdir_if_none = mkdir_if_none
Path.rmtree = rmtree
