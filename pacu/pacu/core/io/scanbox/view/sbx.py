from pacu.util.path import Path
from pacu.profile import manager

opt = manager.instance('opt')

class ScanboxSBXView(object):
    def __init__(self, path):
        self.path = Path(path)
#     def toDict(self):
#         return dict(
#             name = self.path.stem,
#             user = 'Jack',
#             time = str(self.path.created_at),
#             host = '2P',
#             desc = '',
#             mouse = self.path.size.str,
#             package = 'package',
#         )
    def toDict(self):
        return dict(
            path = self.path.relative_to(opt.scanbox_root).str,
            time = str(self.path.created_at),
            size = self.path.size.str,
        )
# testpath = '/Volumes/Users/ht/dev/current/pacu/tmp/Jack/jc6/jc6_1_000_003.sbx'
# r = ScanboxSBXView(testpath)
