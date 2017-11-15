from __future__ import print_function

import sys
import runpy

from . import parser
from . import metavars
from .. import profile

if len(sys.argv) == 1:
    parser.print_help()
    parser.exit()
try:
    args, _ = parser.parse_known_args()
    profile.manager.currents.update(metavars('PROFILE', args))
    runpy.run_module('.'.join((__package__, args.api)),
        init_globals = vars(args), run_name = '__api_main__')
except NotImplementedError:
    print('The command `%s` is still '
        'in development. (not implemented)' % sys.argv[0])
