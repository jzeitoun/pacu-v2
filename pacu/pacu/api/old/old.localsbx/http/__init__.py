from pacu.util.path import Path
from pacu.core.scanbox import adapter

localpath = Path('/Volumes/Users/ht/tmp/pysbx-data')
localsbx = []

for path in localpath.rglob('*.mat'):
    try:
        localsbx.append(adapter.get_meta(path.str))
    except Exception as e:
        print 'Unable to read {}'.format(path.str)
    else:
        print 'Data loaded: {}'.format(path.str)

def get(req):
    data = [
        dict(uid=index, text=Path(sbx.raw.filename).stem)
        for index, sbx in enumerate(localsbx)
    ]
    return dict(data=data)
