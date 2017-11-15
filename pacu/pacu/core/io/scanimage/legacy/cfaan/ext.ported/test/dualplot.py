import numpy as np
from PyQt4 import QtGui

from ext.fcanvas.sfreq import TuningCurveCanvas

main_widget = QtGui.QWidget()
main_widget.setWindowTitle('SF Tuning')
main_widget.move(0, 0)
main_widget.resize(400, 400)
main_widget.show()

sfx = np.linspace(0, 2, 5)
sfy = [0.56, 1.2, 1.79, 3, 2.1]
fff = 1.123
blank = 1.321
tnc = TuningCurveCanvas(
    main_widget,
    sfx,
    sfy,
    fff = fff,
    blank = blank
)
