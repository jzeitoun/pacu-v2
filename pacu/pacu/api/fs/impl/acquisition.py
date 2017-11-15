# destination(situation) determined here

class FSAcquisition(object):
    def __init__(self, path):
        self.path = path
    def __iter__(self):
        return (p for p in self.path.ls()
            if not p.name.startswith('.'))


# X(path) should give me a specific type
