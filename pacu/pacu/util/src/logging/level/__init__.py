from __future__ import absolute_import
from __future__ import print_function

import logging

logging.PRINT = 1
logging.VERBOSE = 5
logging.addLevelName(logging.PRINT, 'PRINT')
logging.addLevelName(logging.VERBOSE, 'VERBOSE')
logging.Logger.verbose = lambda inst, msg, *args, **kwargs:\
    inst.log(logging.VERBOSE, msg, *args, **kwargs)
logging.Logger.print = lambda inst, msg, *args, **kwargs:\
    inst.log(logging.PRINT, msg, *args, **kwargs)

for name in (
    'print'   , # DEV CODING-TIME FREE-FORMAT
    'verbose' , # DEV CODING-TIME
    'debug'   , # DEV RUN-TIME
    'info'    , # SERVICE TRACKING
    'warning' , # DEPRECATION, CATCHABLE
    'error'   , # BOOTSTRAP FAIL, UNCATCHABLE
    'critical'  # SECURITY
    ): setattr(logging.Logger, name[0], getattr(logging.Logger, name))
