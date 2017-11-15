import numpy as np
import matplotlib.gridspec as gridspec

from ext.console import debug
from ext.fcanvas import MPLCanvas
from parse_tuning import Response
from ext.fit.dog import SpatialFrequencyDogFit

class TuningCurveCanvas(MPLCanvas):
    sfdog = None
    def initialize(self):
        self.setWindowTitle('Spatial Frequency Tuning Curve')
        gs0, gs1 = gridspec.GridSpec(1, 2, width_ratios=[4, 1])
        self.ax1 = self.figure.add_subplot(gs0)
        self.ax2 = self.figure.add_subplot(gs1, sharey=self.ax1)
        self.ax1.hold(False)
        self.ax1.set_title('Spatial Frequency', fontsize=12)
        self.ax2.set_title('ETC', fontsize=12)
        self.ax1.tick_params(labelsize=10)
        self.ax1t = self.ax1.twinx()
        self.ax1t.grid(axis='y')
        self.ax1t.tick_params(labelsize=6)
        self.ax2t = self.ax2.twinx()
        self.ax2t.grid(axis='y')
        self.ax2t.tick_params(labelsize=6)

    def replot(self, sfdog):
        sfx, sfy, blank = sfdog.xfreq, sfdog.ymeas, sfdog.blank
        self.ax1.plot(sfx, sfy, '-ok')
        self.ax1.set_xticks(sfx)
        self.ax1.set_xticklabels(['F'] + list(sfx)[1:])
        self.ax2.clear()
        if blank is not None:
            self.ax2.scatter([0], [blank], color='k')
        self.ax2.label_outer()
        self.ax2.set_xticks([-1, 0, 1])
        self.ax2.set_xticklabels(['', 'B', ''])
        self.ax1t.set_ylim(self.ax1.get_ylim())
        self.ax1t.set_yticks(filter(None, sfy))
        self.ax2t.set_ylim(self.ax1.get_ylim())
        self.ax2t.set_yticks(filter(None, [blank]))
        self.draw()

    def replot_dogfit(self, sfdog):
        self.ax1.hold(True)
        self.ax1.plot(*sfdog.dog_xy, color='r')
        self.ax1.set_xticks(sfdog.xfreq)
        self.draw()
        self.ax1.hold(False)

    def updatePlot(self, sfdog):
        self.sfdog = sfdog
        try:
            self.replot(sfdog)
            self.replot_dogfit(sfdog)
        except Exception as e:
            pass
        return self
