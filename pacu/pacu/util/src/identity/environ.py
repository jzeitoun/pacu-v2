import os

from .. import identity

"""
How to get along with fish shell's environment variables.

Setting as universal (i.e. persistent)
    set -Ux NAME VALUE
Setting as global (i.e. current shell instance)
    set -gx NAME VALUE
In-place setting(i.e. current process)
    env NAME=VALUE command ...
Erase variables
    set -e NAME
"""

def make_key(*words):
    PREFIX = identity.name.upper().replace('-', '_')
    WORDS = [word.upper() for word in words]
    return '_'.join([PREFIX] + WORDS)
def get(*words):
    KEY = make_key(*words)
    return KEY, os.environ.get(KEY)
def getval(*words):
    key, val = get(*words)
    return val
def set(val, *words):
    KEY = make_key(*words)
    os.environ[KEY] = val
    return KEY, val
def setdefault(val, *words):
    KEY = make_key(*words)
    if KEY in os.environ:
        return KEY, os.environ[KEY]
    return set(val, *words)

