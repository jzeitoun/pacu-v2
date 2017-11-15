# Written by Hyungtae Kim <hyungtk@uci.edu>, in Nov 2014

import sys

from ext import console

console.on = True

from ext import menubar
from ext import roi_table
from ext import model
from ext import test

from PyQt4 import QtGui

app = QtGui.QApplication(sys.argv)

if len(sys.argv) is 3:
    print 'entry point test...'
    print 'import * from ext.test.%s...' % sys.argv[2]
    exec('from ext.test.%s import *' % sys.argv[2])
else:
    from main import initializeMainGui
    maingui = initializeMainGui()

sys.exit(app.exec_())

