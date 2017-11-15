from pacu.api.fs.impl.item.dir import DirItem
from pacu.api.fs.impl.item.file import FileItem
from pacu.api.fs.impl.item.unknown import UnknownItem

class FSInstantiation(object):
    def __init__(self, paths):
        self.paths = paths
    def __iter__(self):
        return iter(map(self.determine, self.paths))
    def determine(self, path):
        return (
                 DirItem(path)  if path.is_dir()
            else FileItem(path) if path.is_file()
            else UnknownItem(path)
        )
