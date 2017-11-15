from pacu.util.inspect import repr

class Condition(object):
    def __init__(self, x, y, v):
        self.x = x
        self.y = y
        self.v = v
    __repr__ = repr.auto_strict
