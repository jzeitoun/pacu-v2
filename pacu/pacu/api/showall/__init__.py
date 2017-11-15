from .. import subparsers

parser = subparsers.add_parser('showall', help='list all of profiles')
parser.add_argument('contains',
    help='only prints profiles matching with given string.', nargs='?')
