from pprint import pformat

class SectionProxy(object):
    def __init__(self, section, odict):
        self.__dict__ = odict # shadows self.{}
        self.__name__ = section
    def __iter__(self):
        return iter(vars(self))
    def __repr__(self):
        return 'SectionProxy({!r}, OrderedDict(\n{}\n))'.format(
                self.__name__, pformat(vars(self).items())
        )
    def __call__(self, *args, **kwargs):
        return self.__call__(*args, **kwargs) # does not recur
