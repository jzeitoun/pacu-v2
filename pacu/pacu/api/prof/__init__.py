from .. import subparsers

parser = subparsers.add_parser('prof', help='print a profile and exit',
    epilog='''If both `option` and `section` were not given,
    it just prints current profiles.'''
)
parser.add_argument('option', help='a profile to load', nargs='?')
parser.add_argument('section', help='a section to print', nargs='?')
parser.add_argument('-e', dest='edit', help='open vim with target profile')
