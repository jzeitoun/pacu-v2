from pacu.util.inspect import repr
from pacu.api.fs.impl.item.base import BaseItem

class BaseInfoItem(BaseItem):
    classes = 'disabled'
    __repr__ = repr.auto_strict
    def __init__(self, text, classes='', icon=''):
        self.text = text
        self.classes = ' '.join((self.classes, classes))
        self.icon = icon
