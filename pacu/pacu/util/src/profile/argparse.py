import sys

from ..regex.pattern.argparse import optional1

"""
argv like,
argv = 'pacu --db=ephemeral shell --db.echo=off --web.port=12345 --db.port=8761'.split()
"""

def parse_argv(argv=None):
    argv = argv or sys.argv
    return [match.groupdict()
            for match in filter(None, map(optional1.match, argv))]
