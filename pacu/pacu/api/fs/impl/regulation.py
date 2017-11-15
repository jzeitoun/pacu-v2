import itertools
import operator

from pacu.api.fs.impl.item.dir import DirItem
from pacu.api.fs.impl.item.file import FileItem
from pacu.api.fs.impl.item.unknown import UnknownItem
from pacu.api.fs.impl.item.info.trailing import TrailingInfoItem

class FSRegulation(object):
    def __init__(self, items):
        self.items = items
    def __iter__(self):
        return iter(self.makeup(self.sort(self.filter(self.items))))
    def filter(self, items):
        return (item for item in self.items
            if not isinstance(item, UnknownItem))
    def sort(self, items):
        return sorted(items, key=operator.attrgetter('weight', 'name'))
    def makeup(self, items):
        num_files, num_dirs = 0, 0
        for item in items:
            if isinstance(item, DirItem):
                num_dirs += 1
            elif isinstance(item, FileItem):
                num_files += 1
            else:
                pass
            yield item
        if any((num_files, num_dirs)):
            yield TrailingInfoItem('Directory: {}, File: {}'.format(
                num_dirs, num_files), icon='info circle')
        else:
            yield TrailingInfoItem('Nothing in this directory...',
                icon='warning sign')

