from pacu.profile import manager
from pacu.core.io.scanimage.impl import ScanimageIO

opt = manager.instance('opt')

def index_record(year, month, day):
    rec_paths = sorted(
        path.str for path in opt.scanimage_root.ls(
            '{}.{:2}.{:2}/*/*.tif'.format(year, month, day)))
    records = map(ScanimageIO.get_record, rec_paths)
    return dict(year=year, month=month, day=day, records=records)

def index_day(year, month):
    days = sorted(
        set(unicode(path.suffix[1:])
            for path in opt.scanimage_root.ls('{}.{:2}.*'.format(year, month))))
    return dict(year=year, month=month, days=days)

def index_month(year):
    months = sorted(
        set(unicode(path.stem[5:])
        for path in opt.scanimage_root.ls('{}.*'.format(year))
        if path.is_dir()))
    return dict(year=year, months=months)

def index_year():
    years = sorted(set(path.name[:4]
        for path in opt.scanimage_root.ls() if path.is_dir()))
    return dict(years=years)

def get_index(req, year=None, month=None, day=None):
    return index_record (year, month, day) if all((year, month, day)) else \
           index_day    (year, month)      if all((year, month))      else \
           index_month  (year)             if year                    else \
           index_year   ()

def post_session(req, path, session):
    rec = ScanimageIO(path)
    rec.set_session(session).session.create()
    return rec

def delete_session(req, path, session):
    rec = ScanimageIO(path)
    rec.set_session(session).session.remove()
    return rec
