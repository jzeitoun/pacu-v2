import sys
from argparse import ArgumentParser, Action

if sys.argv[0] in ['-c', '-m']:
    sys.argv[0] = 'python -m %s' % __package__

parser = ArgumentParser(
    description = 'PACU v0.0.1',
    epilog = "Contact to: Hyungtae Kim <hyungtk@uci.edu>",
)
group = parser.add_argument_group(
    title='profiles',
    description='''
    You can provide a specific set of profiles for essential configurations.
    It is strongly recommended to go through
    the profile section of the documentation before you use it in production.
    Profiles should be passed in prior to specific API.
    ''')
group.add_argument('--web', metavar='PROFILE',
    help='which profile to use for web')
group.add_argument('--db', metavar='PROFILE',
    help='which profile to use for db')
group.add_argument('--log', metavar='PROFILE',
    help='which profile to use for log')
group.add_argument('--opt', metavar='PROFILE',
    help='which profile to use for opt')
subparsers = parser.add_subparsers(
    title = 'Available APIs',
    dest = 'api',
    metavar = 'API',
    help = 'Description',
    description = '''
        You can get additional help by typing one of below commands.
        Also, it is possible to override current profile by
        passing arguments like `--web.port=12345 --db.echo=false`.
        Make sure these extra arguments should come after specific API.
    ''',
)

def metavars(var, args):
    return {
        action.dest: getattr(args, action.dest)
        for action in parser._actions
        if action.metavar==var}

# API registration
# from . import ping
from . import prof
from . import serve
from . import shell
# from . import query
# from . import vstim
