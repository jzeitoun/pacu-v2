from pacu.api.fs.impl.item.base import BaseItem
from pacu.util.inspect import repr

class FSItem(BaseItem):
    __repr__ = repr.auto_strict
    def __init__(self, path):
        self.path = path
        self.name = path.name
        self.value = path.name
        self.text = path.name
