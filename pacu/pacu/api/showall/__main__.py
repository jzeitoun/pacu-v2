from __future__ import print_function

from ... import profile
from ...util import identity

# profile manager could provide same feature
def findall(contains=None):
    path = identity.path.src.joinpath('profile')
    glob = '*%s*.cfg' % contains.replace('-', '_') if contains else '*.cfg'
    cfgs = path.ls(glob)
    return [cfg.stem.replace('_', '-') for cfg in cfgs]

def main(contains=None):
    print('')
    cfgs = findall(contains=contains)
    print(*cfgs, sep='\n')
    print('\n{} item(s)'.format(len(cfgs)))

if __name__ == '__api_main__':
    main(contains=profile.args.contains)

