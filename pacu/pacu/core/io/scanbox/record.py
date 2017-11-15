from pacu.util.path import Path

class ScanboxRecord(object):
    def __init__(self, path):
        self.path = Path(path)
    def toDict(self):
        return dict(
            name = self.path.stem,
            user = 'Jack',
            time = str(self.path.created_at),
            host = '2P',
            desc = '',
            mouse = self.path.size.str,
            package = 'package',
        )


# testpath = '/Volumes/Users/ht/dev/current/pacu/tmp/Jack/jc6/jc6_1_000_003.sbx'
# r = ScanboxRecord(testpath)

