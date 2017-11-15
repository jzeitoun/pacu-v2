import importlib
from ConfigParser import SafeConfigParser
from collections import namedtuple, OrderedDict
from cStringIO import StringIO

from .. import identity
from ..path import Path
from ..inspect.get import clsname
from ..str.poly import polymorphicStr

ParseFail = namedtuple('ParseFail', 'filename exception')

class SaferConfigParser(SafeConfigParser, object):
    optionxform = str
    def __init__(self, *args, **kwargs):
        super(SaferConfigParser, self).__init__(*args, **kwargs)
        self.failed = []
    def safer_read_files(self, *filenames):
        for filename in filenames:
            try:
                self.read(filename)
            except Exception as e:
                self.failed.append(ParseFail(filename, e))
        return self
    def read_string(self, string, filename=None):
        self.readfp(StringIO(string), filename=filename)
        return self
    @classmethod
    def from_filenames(cls, *filenames):
        return cls().safer_read_files(*filenames)
