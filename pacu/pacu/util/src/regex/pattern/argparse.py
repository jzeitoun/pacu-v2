import re

from .. import preset

optional1 = re.compile(
    r'--(?P<profile>{identifier})\.(?P<key>{identifier})=(?P<val>.+)'.format(
        identifier = preset.identifier
    ), re.VERBOSE|re.UNICODE
)
