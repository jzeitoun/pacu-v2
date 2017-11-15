from ..path import Path

class polymorphicStr(str):
    @property
    def bool(self):
        return self.lower() in ['true', '1', 't', 'y', 'yes', 'on']
    @property
    def int(self):
        return int(self)
    @property
    def float(self):
        return float(self)
    @property
    def list(self):
        return [s.strip() for s in self.split(',')]
    def apply(self, func, *args, **kwargs):
        return func(self, *args, **kwargs)
    def listof(self, type, delim=','):
        return [type(s.strip()) for s in self.split(delim)]
    @property
    def path(self):
        return Path(str(self))
    @property
    def module(self):
        raise NotImplementedError
    @property
    def json(self):
        raise NotImplementedError
    @property
    def ref(self):
        raise NotImplementedError
    @property
    def date(self):
        raise NotImplementedError

def test():
    import pytest
    assert [1, 2, 3] == polymorphicStr('1, 2, 3').listof(int)
    assert ['1', '2', '3'] == polymorphicStr('1, 2, 3').list
    assert [1, 2, 3] == polymorphicStr('1 2 3').listof(int, ' ')
    assert [0.1, 2.0] == polymorphicStr('0.1, 2').listof(float)
    assert 2 == polymorphicStr('2').int
    assert 35.11 == polymorphicStr('35.11').float
    with pytest.raises(ValueError):
        polymorphicStr('35.11').int
    assert 'thisthat' == polymorphicStr('this').apply(
        lambda a, b: a + b, 'that')
