from datetime import datetime

from pacu.util.path import Path
from pacu.util.identity import path
from pacu.util.newtype.snode.node.base import BaseNode
from pacu.util.newtype.snode.abc.mapper import BaseMapper
# from pacu.core.scanbox.mapper.mat import MatMapper
from pacu.core.io.scanbox.impl import ScanboxIO
from pacu.core.io.scanbox.view.info import ScanboxInfoView

class InfoItem(BaseNode):
    mappers = BaseMapper.extend(icon='info circle', classes='disabled')
    def on_map(self, mapping):
        return dict(text=self.data)
class ItemNode(BaseNode):
    def on_map(self, mapping):
        name = self.data.name
        return dict(text=name, value=name)
class DirItem(ItemNode):
    mappers = BaseMapper.extend(icon='folder', classes='fs-dir')
    weight = 10
    checker = Path.is_dir
class SBXFileItem(ItemNode):
    mappers = BaseMapper.extend(icon='file', classes='fs-file')
    weight = 20
    @classmethod
    def check(cls, path):
        return path.str.endswith('.sbx') and path.with_suffix('.mat').is_file()
    def on_map(self, mapping):
        return dict(text=self.data.stem, value=self.data.name)
class TIFFileItem(ItemNode):
    mappers = BaseMapper.extend(icon='file', classes='fs-file')
    weight = 30
    @classmethod
    def check(cls, path):
        return path.str.endswith('.tif')
    def on_map(self, mapping):
        return dict(text=self.data.name, value=self.data.name)
class DirectoryScanForResource(BaseNode):
    routes = (DirItem, SBXFileItem, TIFFileItem)
    sort_keys = ('weight',)
    checker = Path.is_dir
    InfoNode = InfoItem
    def unfold(self):
        return self.data.glob('*')
    def makeup(self, items):
        if items:
            dirs = len(self.context['DirItem'])
            files = len(self.context['SBXFileItem']) + len(self.context['TIFFileItem'])
            yield self.link_info_node('Directory: {}, File: {}'.format(dirs, files))
        else:
            yield self.link_info_node('No resource files is in this directory...')
class SBXMetaItem(BaseNode):
    mappers = BaseMapper.extend(icon='info circle', classes='disabled')
    def on_map(self, mapping):
        return dict(text=self.data)
class FileScanForSBX(BaseNode):
    InfoNode = SBXMetaItem
    checker = ScanboxIO.can_resolve
    def nodes(self):
        self.context['actions'].append('select')
        sbx = ScanboxIO(self.data)
        for key, val in (
            ('Number of frames', sbx.nframes),
            ('Frame rate', sbx.info.framerate),
            ('Size', sbx.data.size),
        ):
            yield self.link_info_node('{}: {}'.format(key, val))
        ctime = datetime.fromtimestamp(sbx.info.path.stat().st_ctime)
        yield self.link_info_node(
            'created at: {!s}'.format(ctime))
        yield self.link(InfoItem,
            'Hit Enter key or click the check icon to select this resource...')
    def on_select(self):
        return dict(data=self.data.with_name(self.data.stem).str)
class FileScanForSCI(BaseNode):
    InfoNode = SBXMetaItem
    # checker = ScanboxIO.can_resolve
    def check(self, path):
        return path.is_file()
    def nodes(self):
        self.context['actions'].append('select')
        ctime = datetime.fromtimestamp(self.data.stat().st_ctime)
        yield self.link_info_node('Tiff file from ScanImage')
        yield self.link_info_node('created at: {!s}'.format(ctime))
        yield self.link(InfoItem,
            'Hit Enter key or click the check icon to select this resource...')
    def on_select(self):
        return dict(data=self.data.with_name(self.data.name).str)

class FSGraph(BaseNode):
    InfoNode = InfoItem
    routes = (
        DirectoryScanForResource,
        FileScanForSBX,
        FileScanForSCI,
    )
    def unfold(self):
        yield Path(self.data)

# print FSGraph(sbxpath).render().to_json()
# qwe = FSGraph(sbxpath.joinpath('JZ5', 'JZ5_000_003.mat')).render().to_json()
# print qwe.render().to_json()
# print qwe.catch()
# print qwe
# qwe = FSGraph(sbxpath.joinpath('fake-error-data.mat')).render().to_json()
# jz5 = '/Volumes/Users/ht/tmp/pysbx-data/JZ5/JZ5_000_003'
# f = FileGroup(jz5)

from pacu.profile import manager

sbxroot = manager.instance('opt').scanbox_root

sbxpath = Path(sbxroot)
# sbxpath = Path('/Volumes/Users/ht/tmp/pysbx-data')
# sbxpath = Path('/Volumes/Recordings/scanbox-jack/my4r_1_3')

def get(req, anchor, *hops, **kwargs):
    action = kwargs.get('action')
    # dest = path.cwd.joinpath(*hops)
    dest = sbxpath.joinpath(*hops)
    try:
        graph = FSGraph(dest)
        return graph.action(action) if action else graph.render().to_json()
    except Exception as e:
        print e
        raise e


# tiff = Path('/Volumes/Gandhi Lab - HT/sci/2014.12.20/x.140801.1/field004.tif')
