# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 16:09:03 2014

@author: kyle
"""

from PyQt4 import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from celldetect import celldetect
from parse_tuning import Response
import cv2

from ext.console import debug
from ext.view.outer_roi import OuterROI, OuterROIOption
from ext.util.calc.neuropil import Neuropil, RatioNeuropil
from ext.util.adapter import response as response_adapter

from scipy.optimize import curve_fit

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
default_trace_color='k' #'k' is black and 'w' is white

class TiffFig(pg.ImageView):

    neuropil_options = dict(
        off = OuterROIOption(m=0, n=0, active=False),
        double = OuterROIOption(m=3, n=2),
        whole = OuterROIOption(m=2, n=1),
    )
    curr_np_option = None

    @classmethod
    def bind_neuropil_action(cls, maingui, agroup, action):
        def on_menu_change():
            checked = agroup.checkedAction()
            action_name = str(checked.text())
            np_option = cls.neuropil_options.get(action_name)
            cls.curr_np_option = np_option
            if maingui.tiffFig:
                maingui.tiffFig.neuropil_option_changed()
        action.triggered[()].connect(on_menu_change)

    def neuropil_option_changed(self):
        for roi in self.rois:
            roi.neuropil_option_changed(self.curr_np_option)
        if self.roi_current:
            self.roi_current.update_responsefig()

    def __init__(self,tiffstack,parent):
        super(TiffFig,self).__init__(parent) ## Create window with ImageView widget
        self.ui.normBtn.setParent(None) # gets rid of 'norm' button that comes with ImageView
        self.ui.roiBtn.setParent(None) # gets rid of 'roi' button that comes with ImageView
        self.tiffstack=tiffstack
        self.setImage(tiffstack) #    imv.setImage(tiffstack, xvals=np.linspace(1., 3., tiffstack.shape[0]))
        self.scene.sigMouseClicked.connect(self.mouseClicked)
        #self.scene.sigMouseMoved.connect(self.mouseMoved)
        self.image=self.getImageItem().image
        self.view.mouseDragEvent=self.mouseDragEvent
        #self.view.wheelEvent=self.wheelEvent
        self.rois=[]
        self.roi_current=None
        coi=self.parent().settings.d['channelOfInterest']-1 # coi = channel of interest
        tiff_for_trace = tiffstack[:,10,10,coi]
        self.traceFig=TraceFig(tiff_for_trace, self)
        self.traceFig.show()
        self.press=None

        #create contours
        if self.parent().persistant['ROIs'] is None:
            if self.parent().settings.d['autodetectROIs']:
                im=self.tiffstack[0:200,:,:,coi].mean(0)
                im=np.transpose(im,(1,0))
                #im=np.flipud(np.fliplr(im))
                contours=celldetect(im)
                for c in contours:
                    ROI(np.array([p[0] for p in c]),self)
        else: #if we loaded ROIs from ED
            rois=self.parent().persistant['ROIs']
            for r in rois:
                ROI(np.array([p[0] for p in r['contour']]),self,r['label'])

        conditions = self.parent().conditions
        if conditions:
            self.responseFig=ResponseFig(self)
            parent.rmax_by_sfreq.updatePlot(tiff_for_trace, conditions, parent.sfreq_meta)

    #    def wheelEvent(self,ev):
    #        ev.accept()
    #        delta=ev.delta()/120
    #        self.jumpFrames(delta)
    #        self.ev=ev

    def get_xy(self,pos):
        p=self.getImageItem().mapFromScene(pos)
        p=p.toPoint()
        x=p.x()
        y=p.y()
        if x<0 or x>self.image.shape[0] or y<0 or y>self.image.shape[1]:
            return False,False
        #print('{},{}'.format(x,y))
        return x,y

    def mouseDragEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            ev.accept()
            x,y=self.get_xy(QtCore.QPoint(ev.scenePos()[0],ev.scenePos()[1]))
            if x is False: return False
            if ev.isStart():
                self.press=np.array([np.array([np.array([x,y])])])
            if ev.isFinish():
                self.press=cv2.approxPolyDP(self.press,0.01*cv2.arcLength(self.press,True),True)
                if len(self.press)>=4:
                    roi=ROI(np.array([p[0] for p in self.press]),self)
            else:
                if self.press[-1][0][0]!=x and self.press[-1][0][1]!=y:
                    self.press=np.append(self.press,np.array([np.array([np.array([x,y])])]),0)
            self.ev=ev

    def mouseClicked(self,pos):
        self.pos=pos
        x,y=self.get_xy(QtCore.QPoint(pos.scenePos()[0],pos.scenePos()[1]))
        if x is False: return False

    def mouseMoved(self,pos):
        x,y=self.get_xy(pos)
        if x is False: return False
    def keyPressEvent(self,ev):
        if ev.key() == QtCore.Qt.Key_Delete:
            if self.roi_current is not None:
                self.roi_current.delete()
                self.roi_current=None

    ##########################################################
    # Injected by Hyungtae Kim <hyungtk@uci.edu>, in Nov 2014, Feb 2015
    # handle an event to change data set based on specific spatial frequency.
    #
    def spatial_frequency_changed(self, index):
        meta = self.parent().sfreq_meta
        if meta:
            meta.sfreq_cursor = index
        if self.roi_current:
            self.roi_current.update_responsefig()
        self.traceFig.update_gray_bars()

    def temporal_frequency_changed(self, index):
        meta = self.parent().sfreq_meta
        if meta:
            meta.tfreq_cursor = index
        if self.roi_current:
            self.roi_current.update_responsefig()
        self.traceFig.update_gray_bars()

class TraceFig(pg.GraphicsWindow):
    def __init__(self,trace,tiffFig):
        super(TraceFig,self).__init__()
        self.tiffFig=tiffFig
        self.setWindowTitle('ceilingfaan - {}'.format(self.tiffFig.parent().settings.d['filename']))
        self.setGeometry(QtCore.QRect(1000, 33, 905, 300))
        self.label = pg.LabelItem(justify='right')
        self.addItem(self.label)
        self.p1 = self.addPlot(row=1, col=0)
        self.p2 = self.addPlot(row=2, col=0)
        self.region = pg.LinearRegionItem()         # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this item when doing auto-range calculations.
        self.region.setZValue(10)
        self.region.sigRegionChanged.connect(self.update)
        self.p1.sigRangeChanged.connect(self.updateRegion)
        self.p2.addItem(self.region, ignoreBounds=True)
        self.p1.setAutoVisible(y=True)
        self.trace = trace
        self.p1data=self.p1.plot(trace, pen="r")
        self.p2data=self.p2.plot(trace, pen=default_trace_color)
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.p1.addItem(self.vLine, ignoreBounds=True)
        self.p1.addItem(self.hLine, ignoreBounds=True)
        self.vb = self.p1.vb
        self.proxy = pg.SignalProxy(self.p1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.region.setRegion([0, 200])
        self.p2.vb.mouseDragEvent=self.mouseDragEvent2
        if self.tiffFig.parent().conditions is not None:
            self.update_gray_bars()

    ##########################################################
    # Modified by Hyungtae Kim <hyungtk@uci.edu>, in Dec 2014
    # Gray bars should support sfreq meta as well as `ResponseFig`
    # I changed name from `addgraybars` - > `update_gray_bars` to let this have right name.
    #
    def clear_gray_bars(self):
        gbars_p1 = [item for item in self.p1.items if hasattr(item, '__graybar__')]
        gbars_p2 = [item for item in self.p2.items if hasattr(item, '__graybar__')]
        for gbp1, gbp2 in zip(gbars_p1, gbars_p2):
            self.p1.removeItem(gbp1)
            self.p2.removeItem(gbp2)

    def update_gray_bars(self):
        self.clear_gray_bars()
        parent = self.tiffFig.parent()
        cond = parent.conditions
        meta = parent.sfreq_meta
        # if meta:
        #     print 'gray bars will be updated along the current sfreq meta by cursor at #%s' % meta.sfreq_cursor
        resp = Response(self.trace, cond, meta)
        for o in resp.orientations:
            for rep in o.reps:
                # print rep.firstFrame, rep.lastFrame
                a1=pg.LinearRegionItem(
                    values=[rep.firstFrame,rep.lastFrame],
                    brush=pg.mkBrush(0, 0, 0, 40), movable=False) #add gray bars
                a1.__graybar__ = True
                self.p1.addItem(a1)
                for l in a1.lines:
                    self.scene().removeItem(l)
                a2=pg.LinearRegionItem(
                    values=[rep.firstFrame,rep.lastFrame],
                    brush=pg.mkBrush(0, 0, 0, 40), movable=False) #add gray bars
                a2.__graybar__ = True
                self.p2.addItem(a2)
                for l in a2.lines:
                    self.scene().removeItem(l)
    def mouseDragEvent2(self,ev):
        ev.ignore() # prevent anything from happening
    def mouseDragEvent1(self,ev):
        ev.ignore() # prevent anything from happening
    def update(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.p1.setXRange(minX, maxX, padding=0)
    def updateRegion(self,window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)

    def mouseMoved(self,evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.p1.sceneBoundingRect().contains(pos):
            mousePoint = self.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            if index > 0 and index < len(self.trace):
                self.label.setText("<span style='font-size: 12pt'>frame={0},   <span style='color: red'>y={1:.1f}</span>".format(index, self.trace[index]))
                self.tiffFig.setCurrentIndex(index)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())

    def update_trace(self,trace):
        self.p1data.setData(trace)
        self.p2data.setData(trace)


class ResponseFig(pg.GraphicsWindow):
    tau = None
    def __init__(self,tiffFig):
        super(ResponseFig,self).__init__()
        self.setGeometry(QtCore.QRect(926, 371, 980, 660))
        self.tiffFig=tiffFig
        self.setWindowTitle('ceilingfaan - {}'.format(self.tiffFig.parent().settings.d['filename']))

        self.c = self.tiffFig.parent().conditions
        start_times=np.array(self.c['ontimes_F'])-self.c['waitInterval_F']
        self.start_times = np.round(start_times).astype('int')
        labelStyle = {'color': 'k', 'font-size': '16pt'}
        self.response = None

        self.p1 = self.addPlot(row=1, col=1)
        self.p1.setLabel('left',u'dF/F0',   **labelStyle) #'ΔF/F₀'
        self.p1.setLabel('bottom','Orientation of Stimulus', **labelStyle)
        self.p1.setFixedWidth(680)

        ##########################################################
        # Modified by Hyungtae Kim <hyungtk@uci.edu>, in Oct 2015
        # We are having another plot next to main plot `p1`.
        #
        self.p4 = self.addPlot(row=1, col=2)
        self.p4.setLabel('left',  u'F', **labelStyle)
        self.p4.setLabel('bottom',u'Decay', **labelStyle)
        #
        ##########################################################

        #self.p1.setLabel
        self.p2 = self.addPlot(row=2, col=2)
        self.p2.disableAutoRange(axis=0)
        self.p3  = self.addPlot(row=2, col=1)
        self.p3.getAxis('bottom').setTickFont(pg.QtGui.QFont('Arial',12))
        self.p3.getAxis('left').setTickFont(pg.QtGui.QFont('Arial',12))
        self.show()

    def update_tau_at_max_orientation(self, pi):

        pi.plot(clear=True)
        pi.disableAutoRange()

        meta = self.tiffFig.parent().sfreq_meta
        ori = self.response.max_orientation
        idx = self.response.max_orientation_index

        pen = pg.mkPen('r', width = 2)
        PEN = pg.mkPen('b', width = 2)

        off_times = np.array(self.c['ontimes_F']) + self.c['waitInterval_F']
        off_times = np.round(off_times).astype('int')

        x0 = off_times[idx]
        x = np.arange(x0, x0 + len(ori.reps[0].offtime_trace))

        for rep in ori.reps:
            try:
                pi.plot(x, rep.offtime_trace, pen=0.5)
            except:
                # HT 03 DEC 2015
                pi.plot(x[:len(rep.offtime_trace)], rep.offtime_trace, pen=0.5)
                debug.enter()

        y = np.array([rep.offtime_trace for rep in ori.reps]).mean(0)
        pi.plot(x, y, pen=pen)

        # a is scale
        # b is frame shift
        # d is offset
        # tau is 1 / c

        def func(x, a, b, c, d):
            return a*np.exp(-c*(x-b))+d
        try:
            print 'X:', x
            print 'Y:', y
            popt, pcov = curve_fit(func, x, y, [100,400,0.001,0])
        except Exception as e:
            print 'monoexponential fitting error', type(e), e
        else:
            framerate = self.c['captureFrequency']
            c = popt[2]
            self.tau = 1.0 / (framerate * c)
            print 'tau: ' + str(self.tau)
            pi.plot(x, func(x, *popt), pen=PEN)

        mov = self.response.max_orientation_value
        pi.setLabel('bottom', u'Decay at %s' % mov)
        pi.autoRange()
        # debug.enter()

    def update_response(self,response):
        self.response=response

        ############################################
        #### p1
        i=0 #this is the index of the orientation
        self.p1.plot(clear=True)
        self.p1.disableAutoRange()
        for o in self.response.orientations:
            x0=self.start_times[i]
            x=np.arange(x0,x0+len(o.reps[0].baseline_trace))
            for rep in o.reps:
                if len(x)==len(rep.baseline_trace):
                    self.p1.plot(x,rep.baseline_trace, pen=.5)
            if hasattr(o,'meanbaseline_trace') and len(x)==len(o.meanbaseline_trace):
                self.p1.plot(x,o.meanbaseline_trace,pen=pg.mkPen('r',width=2))

            x0+=len(x)
            x=np.arange(x0,x0+int(len(o.reps[0].trace)))
            a=pg.LinearRegionItem(values=[x[0],x[-1]],brush=pg.mkBrush(0, 0, 0, 40), movable=False) #add gray bars
            self.p1.addItem(a)
            for l in a.lines:
                self.scene().removeItem(l)
            for rep in o.reps:
                self.p1.plot(x,rep.trace,pen=.5)
            self.p1.plot(x,o.meantrace,pen=pg.mkPen('r',width=2))
            #self.p1.axvspan(x[1], x[-1], facecolor='gray', alpha=0.1) #creates the colored bars
            i+=1
        self.p1.autoRange()
        offset=int(self.c['waitInterval_F']+np.round(self.c['duration_F'])/2)
        interval=int(self.c['condition_F'])
        tics=[]
        for i in range(len(self.c['orientations'])):
            tics.append(offset+interval*i)
        orients=[str(int(i)) for i in self.c['orientations']]
        tics=[[(tics[i],orients[i]) for i in range(len(tics))]]
        self.p1.getAxis('bottom').setTicks(tics)
        self.p1.getAxis('bottom').setTickFont(pg.QtGui.QFont('Arial',12))
        self.p1.getAxis('left').setTickFont(pg.QtGui.QFont('Arial',12))

        self.update_tau_at_max_orientation(self.p4)

        ############################################
        ########  show polar plot

        # self.p3.plot(theta,amplitudes,pen=pg.mkPen('k', width=2))
        # self.p3.plot(self.response.meanresponses_fit[0],self.response.meanresponses_fit[1],pen=pg.mkPen('r', width=2))

        theta=np.array(self.c['orientations'])
        theta=theta.tolist()
        theta.append(360)
        amplitudes=self.response.meanresponses[:]
        amplitudes.append(amplitudes[0])
        amp=np.asarray(amplitudes)
        amp[amp<0]=0 # hide all negative values
        self.p2.plot(clear=True)
        self.p2.setAspectLocked()
        self.p2.setTitle('OSI = {:.4f} DSI= {:.4f} CV= {:.4f}'.format(self.response.OSI,self.response.DSI, self.response.CV), size='17px')

        # Add polar grid lines
        #self.p2.addLine(x=0, pen=0.6) #this draws horizontal axis
        #self.p2.addLine(y=0, pen=0.6) #this draws vertical axis
        for r in np.linspace(0,max(amp),4):
            circle = pg.QtGui.QGraphicsEllipseItem(-r, -r, r*2, r*2)
            circle.setPen(pg.mkPen(0.6))
            self.p2.addItem(circle)
        self.p2.getAxis('bottom').hide()
        self.p2.getAxis('left').hide()
        # Transform to cartesian and plot
        x = amp * np.cos(np.deg2rad(theta))
        y = amp * np.sin(np.deg2rad(theta))
        self.p2.plot(x,y,pen=pg.mkPen('k', width=2))

        self.p2.plot(
            self.response.meanresponses_fit[1] * np.cos(np.deg2rad(self.response.meanresponses_fit[0])),
            self.response.meanresponses_fit[1] * np.sin(np.deg2rad(self.response.meanresponses_fit[0])),
            pen=pg.mkPen('r', width=2))

        self.p2.setRange(xRange=(-max(amp),max(amp)))
        self.p2.setRange(yRange=(-max(amp),max(amp)))

        ############################################
        ########  show gaussian fit plot
        self.p3.plot(clear=True)
        orients=[str(int(i)) for i in self.c['orientations']]
        self.p3.plot(theta,amplitudes,pen=pg.mkPen('k', width=2))
        self.p3.plot(self.response.meanresponses_fit[0],self.response.meanresponses_fit[1],pen=pg.mkPen('r', width=2))
        tics=[]
        for i in range(len(self.c['orientations'])):
            tics.append(offset+interval*i)
        tics=[[(int(orients[i]),orients[i]) for i in range(len(tics))]]
        self.p3.getAxis('bottom').setTicks(tics)
        self.p3.showGrid(x=True,y=True,alpha=.4)
                #SPG 072314 plots sigma, preferred orientation, and max response value

        ##########################################################
        # Modified by Hyungtae Kim <hyungtk@uci.edu>, in Nov 2014
        # To have better formatting and readability support with arbitrary variables.
        #
        sfreq_meta = self.tiffFig.parent().sfreq_meta

        variable_header = 'sigma= {:.4f} Opref= {:.4f} Rmax= {:.4f} Residual= {:.4f}'.format(
            self.response.sigma,
            self.response.Opref,
            self.response.Rmax,
            self.response.residual
        )
        sfreq_meta = self.tiffFig.parent().sfreq_meta
        if sfreq_meta:
            variable_header += ' sfreq= {:.2f}'.format(sfreq_meta.cur_sfreq)
        self.p3.setTitle(variable_header , size='18px')

        #self.gaussianfitax.set_xticks(theta)



class RoiLabelEditor(QtGui.QLineEdit):
    def __init__(self, roi, parent):
        super(RoiLabelEditor, self).__init__(parent)
        self.roi=roi
        self.setText(roi.label)
        self.show()
        self.returnPressed.connect(self.submit)
    def submit(self):
        self.roi.label=str(self.text())
        self.delete()
    def delete(self):
        self.setParent(None)


class ROI(pg.PolyLineROI):

    def neuropil_option_changed(self, option):
        if self.outer:
            self.outer.neuropil_option_changed(option)

    def __init__(self, positions, tiffFig,
                 label='Roi Label', preview=False):
        super(ROI,self).__init__(positions,closed=True)

        self.tiffFig=tiffFig
        self.outer = OuterROI.new(self, positions)
        self.sigRegionChangeFinished.connect(self.regionChangeFinished)
        self.tiffFig.rois.append(self)
        self.outer.inner_will_append_view(self.tiffFig.view)
        self.tiffFig.view.addItem(self)

        self.label=label
        self.labelEditor=None
        self.conditions=tiffFig.parent().conditions
        self.trace=self.getTrace()
        self.preview = preview

        if preview:
            for segment in self.segments:
                segment.setPen(dict(color='b', width=2))

        if not preview and self.conditions is not None:
            sfreq_meta = self.tiffFig.parent().sfreq_meta
            self.response=Response(self.trace,self.conditions, sfreq_meta)
        self.pts=self.getPoints()

    def regionChangeFinished(self, itself):
        self.outer.inner_did_change_region(self.tiffFig.curr_np_option)
        self.pts=self.getPoints()

    ##########################################################
    # Injected and modified by Hyungtae Kim <hyungtk@uci.edu>, in Nov 2014
    # I extracted a part of updating a response figure in `mouseClickEvent` and wrapped
    # it as a new function `update_responsefig` in order to call from another event.
    #
    def update_responsefig(self):
        self.trace, npix =self.getTraceWithNeuropil()
        self.tiffFig.traceFig.update_trace(self.trace)

        if self.conditions is not None:
            parent = self.tiffFig.parent()
            sfreq_meta = parent.sfreq_meta
            self.response = Response(self.trace, self.conditions, sfreq_meta)
            self.tiffFig.responseFig.update_response(self.response)
            parent.rmax_by_sfreq.updatePlot(self.trace, self.conditions, sfreq_meta)
            stats = dict(sfreq_meta.make_analysis_data(self.response), npix=npix)

            stats['osi'] = self.response.OSI
            stats['cv'] = self.response.CV
            stats['dsi'] = self.response.DSI
            stats['sigma'] = self.response.sigma
            stats['opref'] = self.response.Opref
            stats['rmax'] = self.response.Rmax
            stats['resi'] = self.response.Residual
            stats['tau'] = self.tiffFig.responseFig.tau

            if sfreq_meta.has_blank:

                response_wo_neuropil = Response(self.getTrace(), self.conditions, sfreq_meta)
                blank = response_wo_neuropil.blank
                #mean_of_fs = np.mean([rep.just_baseline_trace.mean() for rep in blank.reps]) DXF 11/25
                mean_of_fs = np.mean([rep.just_trace.mean() for rep in blank.reps])
                #stats['mfs_npix'] = mean_of_fs / npix DXFV changed 11/25 because mean_of_fs is already nromalized to the normal of pixels
                stats['mfs_npix'] = mean_of_fs

            parent.stats.updateAnalysis(**stats)

        if self.tiffFig.roi_current is not None:
            if self.tiffFig.roi_current.labelEditor is not None:
                self.tiffFig.roi_current.labelEditor.delete()
            for segment in self.tiffFig.roi_current.segments:
                segment.setPen('b' if self.preview else 'w')
        for segment in self.segments:
            segment.setPen('r')
        self.tiffFig.roi_current=self
        self.labelEditor=RoiLabelEditor(self,self.tiffFig)
        # response_adapter.to_blank_and_orientations(self.response)

    def mouseClickEvent(self,ev):
        if ev.button() == QtCore.Qt.RightButton:
            ev.accept()
        elif ev.button() == QtCore.Qt.LeftButton:
            ev.accept()
            self.update_responsefig()
        else:
            ev.ignore()
    def getPoints(self):
        pts=self.getLocalHandlePositions()
        shifted=self.viewPos().toPoint()
        pts=[[int(p[1].x()), int(p[1].y())] for p in pts]
        pts=[[p[0]+shifted.x(), p[1]+shifted.y()] for p in pts]
        return pts

    def getTraceWithNeuropil(self):
        channel_of_interest = self.tiffFig.parent().settings.d['channelOfInterest']-1 # coi = channel of interest
        channeled_stack = self.tiffFig.tiffstack[:,:,:,channel_of_interest]
        stack_length = len(channeled_stack)

        roi_trace = np.zeros(stack_length)
        cell_trace = np.zeros(stack_length)
        neuropil_trace = np.zeros(stack_length)

        cell_contour = np.array(self.getPoints()).reshape((-1, 1, 2))[:, :, [1, 0]]
        cell_mask = np.zeros(channeled_stack.shape[1:], np.uint8)
        cv2.drawContours(cell_mask, [cell_contour], 0, 255, -1)

        cell_index = self.tiffFig.rois.index(self)
        cells = [np.array(roi.getPoints()) for roi in self.tiffFig.rois]
        option = self.tiffFig.curr_np_option
        print 'before get neuropi mask'
        neuropil_mask = RatioNeuropil(cells, option
                    ).get_single_neuropil(channeled_stack.shape[1:], cell_index)

        for t in np.arange(stack_length):
            mean_cell = cv2.mean(channeled_stack[t, ...], cell_mask)[0]
            mean_neuropil = cv2.mean(channeled_stack[t, ...], neuropil_mask)[0]
            roi_trace[t] = mean_cell - 0.7*mean_neuropil #r determined to be 0.7 by DXFV & SG 11/25/2015
            cell_trace[t] = mean_cell
            neuropil_trace[t] = mean_neuropil

        trace_info = (
            'NEUROPIL has collision ? {}\n'
            'NEUROPIL has {} pixel(s)...\n'
            'mean of CELL_INTENSITY: {}\n'
            'mean of NEUROPIL_INTENSITY: {}\n'
            'mean of TRACE(CELL - 0.7*NEUROPIL): {}\n'
            'max of TRACE(CELL - 0.7*NEUROPIL): {}\n'
            'min of TRACE(CELL - 0.7*NEUROPIL): {}\n'
            ).format(
                '<NOT SUPPORTED>',
                (neuropil_mask > 0).sum(),
                cell_trace.mean(),
                neuropil_trace.mean(),
                roi_trace.mean(),
                roi_trace.max(),
                roi_trace.min(),
            )

        return roi_trace, (cell_mask>0).sum()

    def getTrace(self):
        channel_of_interest = self.tiffFig.parent().settings.d['channelOfInterest']-1 # coi = channel of interest
        channeled_stack = self.tiffFig.tiffstack[:,:,:,channel_of_interest]
        stack_length = len(channeled_stack)
        roi_trace = np.zeros(stack_length)

        cell_contour = np.array(self.getPoints()).reshape((-1, 1, 2))[:, :, [1, 0]]
        cell_mask = np.zeros(channeled_stack.shape[1:], np.uint8)
        cv2.drawContours(cell_mask, [cell_contour], 0, 255, -1)

        # cell_index = self.tiffFig.rois.index(self)
        # print cell_index
        # debug.enter()
        # neuropil_mask = Neuropil(cell_contour[:,0,:], 9).get_masked_neuropil(channeled_stack.shape[1:], cell_index)

        # contour_neuropil = np.array([
        #     [[point.y(), point.x()]] for point in self.outer.get_polygon()
        # ])

        # mask_neuropil = mask.copy() # also make a neuropil mask as a circle that extends out from beyond the ROI by 20 ums

        # if contour_neuropil.any():
        #     cv2.drawContours(mask_neuropil, [contour_neuropil], 0, 255, -1)
        #     xored_np_mask = mask ^ mask_neuropil
        # else:
        #     xored_np_mask = mask_neuropil

        for t in np.arange(stack_length):
            mean_cell = cv2.mean(channeled_stack[t, ...], cell_mask)[0]
            # roi_trace[t] = mean_cell
            mean_neuropil = 0 #cv2.mean(channeled_stack[t, ...], xored_np_mask)[0]
            roi_trace[t] = mean_cell - 0.7*mean_neuropil #roi_trace[t] = mean_cell - 0.7*mean_neuropil
            # print 'cell intensity: {}, neorupil intensity: {}\niCell - 0.7*iNeorupil: {}\n'.format(mean_cell, mean_neuropil, roi_trace[t])
        return roi_trace # updated trace for ROI

    def delete(self):
        if self.labelEditor is not None:
            self.labelEditor.delete()
        if self.outer:
            self.outer.inner_will_delete()
            self.scene().removeItem(self.outer)
            self.outer = None
        self.tiffFig.rois.remove(self)
        self.scene().removeItem(self)
    def getpersistant(self):
        roi=dict()
        roi['contour']=np.array([np.array([np.array([p[0],p[1]])]) for p in self.pts ])
        roi['label']=self.label
        if self.conditions is not None:
            roi['OSI']=self.response.OSI
            roi['ODI']=self.response.DSI
        return roi


#def get_tiffstack():
#    filename="C:/Users/kyle/Desktop/recordings/Kyle/2014.01.09/gcamp6-flex-visstim005.tif"
#    filename="C:/Users/kyle/Desktop/recordings/Ethan/2013.05.14/spot11_contraopen011.tif"
#    tif=tifffile.TIFFfile(filename)
#    tiffstack = tif.asarray()
#    data=tiffstack[1::2]
#    tif.close()
#    return data
def main():
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.resize(800,800)
    tiffstack=get_tiffstack()
    tiffstack=np.transpose(tiffstack,(0,2,1))
    imv=TiffFig(tiffstack,None)
    win.setCentralWidget(imv)
    win.setGeometry(QtCore.QRect(20, 372, 646, 645))
    win.show()
    win.setWindowTitle('ceilingfaan')
if __name__=='__main__':
    main()








