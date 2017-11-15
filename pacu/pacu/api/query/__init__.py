from .. import subparsers

parser = subparsers.add_parser('query', help='query a model over database',
    epilog='''This command is basically equivalent to `db read MODEL`,
    `query` is just a shorthand. Also,
    You can have table name information by passing no arguments.'''
)
parser.add_argument('model', help='a model to query', nargs='?')
parser.add_argument('id', help='query a specific entity',
        default=0, type=int, nargs='?')
