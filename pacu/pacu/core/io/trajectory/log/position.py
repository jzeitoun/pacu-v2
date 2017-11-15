import re
import operator
from collections import namedtuple

re_position = re.compile(r'''
    (?P<ts>{digits}{dot}{digits})
    {delim}
    position
    {delim}
    (?P<x>{sign}{digits}{dot}{digits})
    {delim}
    (?P<y>{sign}{digits}{dot}{digits})
    {delim}
    (?P<z>{sign}{digits}{dot}{digits})
'''.format(
    digits = r'\d+',
    dot    = r'\.',
    delim  = r',\s',
    sign   = r'-?',
), re.VERBOSE)

class Position(namedtuple('Position', 'ts, x, y, z')):
    @classmethod
    def from_lines(cls, lines):
        return [
            cls(*map(float, pos.groups()))
            for pos in map(re_position.match, lines) if pos
        ]
