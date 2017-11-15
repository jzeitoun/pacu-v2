from .. import subparsers

epilog = '''
The `serve` API heavily relies on all the profiles such as `log`, `web`, `db`.
So it is manager's responsibility to setup appropriate profiles
based on its operational context.
Main help has the information how you specify those profiles.
'''
parser = subparsers.add_parser('serve', help='run application as a server', epilog=epilog)
