from .. import subparsers

parser = subparsers.add_parser('ping',
    help='print simple data along with predefined scripts',
    epilog='''You can think of this command as a tiny code snippet executor.
    Mainly this command is used for arbitrary API request from front-end.
    Complex request should be made via `service` machinery in the core package.
    For RESTful access, consider using `query` command.
    '''
)
parser.add_argument('script', help='a script to run', nargs='?')
parser.add_argument('args', help='*argument', nargs='*')
