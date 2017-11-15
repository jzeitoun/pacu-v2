from pathlib import Path
from snode.node.base import BaseNode
from snode.abc.mapper import BaseMapper

class SUIMapper(BaseMapper):
    def vars(self, data, anchor, context):
        pass
class InfoItem(BaseNode):
    mappers = (SUIMapper,)
class FSDirItem(BaseNode):
    weight = 10
    checker = Path.is_dir
class FSFileItem(BaseNode):
    weight = 20
    def check(self, that):
        return that.is_file() and not that.name.startswith('.')
class DirectoryScan(BaseNode):
    routes = (FSDirItem, FSFileItem)
    sort_keys = ('weight',)
    checker = Path.is_dir
    InfoNode = InfoItem
    def unfold(self):
        return self.data.glob('*')
    def induce(self):
        yield self.link_info_node('let us go')
    def makeup(self, items):
        yield self.link_info_node('{} items'.format(len(items)))
class FSGraph(BaseNode):
    routes = (
        DirectoryScan,
        # FileMetaScan,
        # ScanboxMetaScan
    )
    def unfold(self):
        yield Path(self.data)

# a = FSGraph('/Volumes/Users/ht/tmp/pysbx-data').render()

# class FileStat(BaseNode):
#     mappers = BaseMapper.extend(icon='info circle', classes='disabled')
#     def on_map(self, mapping):
#         return dict(text=self.fmt.format(self.data))
# 
# class FileScan(BaseNode):
#     checker = Path.is_file
#     def nodes(self):
#         size, atime, mtime, ctime = self.data.lstat()[-4:]
#         yield self.link(FileStat, size , fmt='Size: {} byte(s)')
#         yield self.link(FileStat, atime, fmt='Accessed at: {}')
#         yield self.link(FileStat, mtime, fmt='Modified at: {}')
#         yield self.link(FileStat, ctime, fmt='Created at: {}')
