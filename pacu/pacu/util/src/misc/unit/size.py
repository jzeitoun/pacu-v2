import functools
import operator

units = [' ', 'kilo', 'mega', 'giga', 'peta', 'exa', 'zetta']
units_schema = list(reversed([
    (
        functools.reduce(operator.mul, [1000] * index, 1),
        next(iter(name)).upper().strip()
    )
    for index, name in enumerate(units)
])) # each item will be (scale, name, symbol)

class SizeUnit(int):
    @property
    def str(self):
        return str(self)
    def __str__(self):
        for scale, symbol in units_schema:
            if abs(self) < scale:
                continue
            fnum = '{:.2f}'.format(self.__truediv__(scale))
            return ''.join((fnum.rstrip('0').rstrip('.'), symbol, 'B'))
    def __repr__(self):
        return '{}({}) # {}'.format(type(self).__name__, int(self), self)
