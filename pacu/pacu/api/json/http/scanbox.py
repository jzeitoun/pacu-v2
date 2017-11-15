from pacu.profile import manager
from pacu.core.io.scanbox.impl import ScanboxIO

opt = manager.instance('opt')

def index_meta(mouse, day):
    io_paths = sorted(set(
        path.with_suffix('.io')
        for path in opt.scanbox_root.joinpath(mouse, day).ls('*.sbx')
        if path.is_file()))
    ios = map(ScanboxIO, io_paths)
    return dict(mouse=mouse, day=day, io_attrs_set=[r.attributes for r in ios])

def index_day(mouse):
    days = sorted(set(path.name
        for path in opt.scanbox_root.joinpath(mouse).ls()
        if path.is_dir()))
    return dict(mouse=mouse, days=days)

def index_mouse():
    mice = sorted(set(path.name
        for path in opt.scanbox_root.ls()
        if path.is_dir()))
    return dict(mice=mice)

def get_index(req, mouse=None, day=None):
    return index_meta(mouse, day) if mouse and day else \
           index_day(mouse) if mouse else \
           index_mouse()
