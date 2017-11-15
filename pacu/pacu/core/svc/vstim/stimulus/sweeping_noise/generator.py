from __future__ import division

import numpy as np
from scipy import io
from scipy import signal
from scipy import special
import matplotlib.cm as cm

from pacu.core.svc.vstim.stimulus.sweeping_noise.unitconv import UnitConverter

def get_bandwidth(distance, deg):
    # to get opposite with `distance` as adjacent deg as `theta`
    return np.tan(np.deg2rad(deg))*distance

def mat(*names):
    mat = io.loadmat('ht-delme.mat', squeeze_me=True)
    return mat.get(names[0]) if len(names) == 1 else [
        mat.get(name) for name in names
    ]

def fspecial_gaussian(shape, sigma=0.5):
    """
    2D gaussian mask - should give the same result as MATLAB's
    fspecial('gaussian',[shape],[sigma])
    """
    m,n = [(ss-1.)/2. for ss in shape]
    y,x = np.ogrid[-m:m+1,-n:n+1]
    h = np.exp( -(x*x + y*y) / (2.*sigma*sigma) )
    h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh
    return h

class SweepingNoiseGenerator(object):
    moviedata = None
    def __init__(self,
            max_spat_freq = 0.05,
            max_temp_freq = 4,
            contrast = 0.5,
            binary_threshold = 0,
            rotation = 0,
            bandfilter= 0, # is gaussian
            duration = 300,
            bandwidth = 5,
            viewwidth = 0,
            # if framerate is given a float, generator will take forever.
            framerate = 30,
            contr_period = 10,
            imsize = 64,
            # imageMag = 18,
            screenWidthCm = 33.169, # from 15.4 inch diagonal inch MBPR 15 
            screenHeightCm = 20.731, # from 15.4 inch diagonal inch MBPR 15 
            screenWidthPix = 1440,
            screenHeightPix = 900,
            viewport_x = None,
            viewport_y = None,
            screenDistanceCm = 25,
            eyepoint_x = 0.5,
            use_random = True,
        ):
        self.max_spat_freq = max_spat_freq
        self.max_temp_freq = max_temp_freq
        self.contrast = contrast
        self.binary_threshold = binary_threshold
        self.rotation = rotation
        self.bandfilter = bandfilter
        self.duration = duration
        self.bandwidth = bandwidth
        self.viewwidth = viewwidth
        self.framerate = framerate
        self.contr_period = contr_period
        self.imsize = imsize
        # self.imageMag = screenWidthPix/imsize
        self.screenWidthCm = screenWidthCm
        self.screenHeightCm = screenHeightCm
        self.screenWidthPix = screenWidthPix
        self.screenHeightPix = screenHeightPix
        self.viewport_x = viewport_x or screenWidthPix
        self.viewport_y = viewport_y or screenHeightPix
        self.screenDistanceCm = screenDistanceCm
        self.eyepoint_x = eyepoint_x
        self.use_random = use_random
        print '\n======================init params========================'
        print 'max sfreq', self.max_spat_freq
        print 'max tfreq', self.max_temp_freq
        print 'contrast', self.contrast
        print 'binary_threshold', self.binary_threshold
        print 'rotation', self.rotation
        print 'band filter', self.bandfilter
        print 'duration', self.duration
        print 'bandwidth', self.bandwidth
        print 'viewwidth', self.viewwidth
        print 'framerate', self.framerate
        print 'cont period', self.contr_period
        print 'imsize', self.imsize
        # print 'imageMag', self.imageMag
        print 'screen width/height cm ', self.screenWidthCm, self.screenHeightCm
        print 'screen width/height pix ', self.screenWidthPix, self.screenHeightPix
        print 'viewport xy ', self.viewport_x, self.viewport_y
        print 'screen dist cm', self.screenDistanceCm
        print 'eyepoint_x', self.eyepoint_x
        print 'use random?', self.use_random
        print '======================init params========================\n'
        is_azi = rotation in [1, 3]
        print 'is azimuth?', is_azi
        self.uc = UnitConverter(
            self.screenWidthPix, self.screenHeightPix,
            self.screenWidthCm, self.screenHeightCm,
            self.screenDistanceCm, self.bandwidth,
            self.imsize, is_azi,
            self.viewport_x, self.viewport_y
        )
        self.uc.show()
    def stim_to_movie(self):
        imsize = self.imsize
        nframes = int(np.ceil(self.duration*self.framerate))

        # cm_per_deg = self.screenWidthCm/self.uc.width_deg
        # pix_per_cm = self.screenWidthPix/self.screenWidthCm
        # final size after image got enlarged
        # I think imageMag should be calculated automatically.
        # degperpix = self.uc.width_deg/self.screenWidthPix
        degperpix_scaled = self.uc.upscaled.deg_per_pix
        # bandwidth_cm = get_bandwidth(self.screenDistanceCm, self.bandwidth)
        # bandwidth_pix_scaled = bandwidth_cm * pix_per_cm / self.imageMag

        # print 'cm per deg', cm_per_deg
        print 'screnwidthdeg', self.uc.width_deg
        # print 'degperpix', degperpix
        print 'deg per pix scaled', degperpix_scaled
        # print 'bandwidth_pix_scaled', bandwidth_pix_scaled
        # print 'bandwidth_cm', bandwidth_cm

        nyq_pix = 0.5
        nyq_deg = nyq_pix/degperpix_scaled
        freqInt_deg = nyq_deg / (0.5*imsize)
        freqInt_pix = nyq_pix / (0.5*imsize)
        nyq = self.framerate/2.0
        tempFreq_int = nyq/(0.5*nframes)

        # Cutoffs in terms of frequency intervals
        tempCutoff = np.round(self.max_temp_freq/tempFreq_int)
        maxFreq_pix = self.max_spat_freq*degperpix_scaled
        spatCutoff = np.round(maxFreq_pix / freqInt_pix) #/2

        # generate frequency spectrum (invFFT)
        alpha = -1
        offset = 3
        range_mult = 1

        # for noise that extends past cutoff parameter (i.e. if cutoff = 1sigma)
        spaceRange = np.arange(
                imsize/2 - range_mult*spatCutoff,
                imsize/2 + range_mult*spatCutoff + 1,
        ) + 1
        tempRange = np.arange(
                nframes/2 - range_mult*tempCutoff,
                nframes/2 + range_mult*tempCutoff + 1,
        ) + 1
        [x,y,z] = np.meshgrid(
            np.arange(-range_mult*spatCutoff, range_mult*spatCutoff + 1),
            np.arange(-range_mult*spatCutoff, range_mult*spatCutoff + 1),
            np.arange(-range_mult*tempCutoff, range_mult*tempCutoff + 1)
        )

        use = np.multiply(
            (
                ((x**2 + y**2) <= (spatCutoff**2))
                    &
                ((z**2) < (tempCutoff**2))
            ),
            (
                np.sqrt(np.add(x**2 + y**2, offset))**alpha
            )
        )
        invFFT = np.zeros([imsize, imsize, nframes], dtype=np.dtype('complex'))
        mu = np.zeros([spaceRange.shape[0], spaceRange.shape[0], tempRange.shape[0]])
        sig = np.ones([spaceRange.shape[0], spaceRange.shape[0], tempRange.shape[0]])

        complex_num = 0+1j
        if self.use_random:
            normal_random_distribution = np.random.normal(mu, sig)
        else:
            normal_random_distribution = np.load('predef-normal-distribution.npy')
        if self.use_random:
            sample = np.random.random_sample([
                int(spaceRange.size), int(spaceRange.size), int(tempRange.size)
            ])
        else:
            sample = np.load('predef-sample.npy')

        mult1 = use*normal_random_distribution
        mult2 = np.exp(2*np.pi*complex_num*sample)
        self.mult1 = mult1
        self.mult2 = mult2
        try:
            invFFT[
                spaceRange[0]:spaceRange[-1]+1,
                spaceRange[0]:spaceRange[-1]+1,
                tempRange[0]:tempRange[-1]+1
            ] = np.multiply(mult1, mult2)
        except ValueError as e:
            raise ValueError(
                'Unable to create blobs by {} spatial frequency with {} image size. '
                'Please increase image size.'
                .format(self.max_spat_freq, self.imsize)
        )
        # in order to get real values for image, need to make spectrum symmetric
        fullspace = np.arange(-range_mult*spatCutoff, range_mult*spatCutoff + 1)
        halfspace = np.arange(1, range_mult*spatCutoff + 1)
        halftemp  = np.arange(1, range_mult*tempCutoff + 1)

        fullspace_add = imsize/2 + fullspace + 1
        fullspace_sub = imsize/2 - fullspace + 1
        halfspace_add = imsize/2 + halfspace + 1
        halfspace_sub = imsize/2 - halfspace + 1

        halftemp_add = np.round(nframes/2) + halftemp + 1
        halftemp_sub = np.round(nframes/2) - halftemp + 1

        invFFT[
            fullspace_add[0]:fullspace_add[-1]+1,
            fullspace_add[0]:fullspace_add[-1]+1,
            halftemp_add[0]:halftemp_add[-1]+1
        ] = np.conjugate(invFFT[
                fullspace_sub[-1]:fullspace_sub[0]+1,
                fullspace_sub[-1]:fullspace_sub[0]+1,
                halftemp_sub[-1]:halftemp_sub[0]+1])
        invFFT[
            fullspace_add[0]:fullspace_add[-1]+1,
            halfspace_add[0]:halfspace_add[-1]+1,
            nframes/2+1
        ] = np.conjugate(invFFT[
                fullspace_sub[-1]:fullspace_sub[0]+1,
                halfspace_sub[-1]:halfspace_sub[0]+1,
                nframes/2+1])
        invFFT[
            halfspace_add[0]:halfspace_add[-1]+1,
            imsize/2+1,
            nframes/2+1
        ] = np.conjugate(invFFT[
                halfspace_sub[-1]:halfspace_sub[0]+1,
                imsize/2+1,
                nframes/2+1])

        shiftinvFFT = np.fft.ifftshift(invFFT)
        imraw = np.fft.ifftn(shiftinvFFT).real
        immax = (imraw.std())/self.contrast
        immin = -1*immax
        imscaled = (imraw-immin-imraw.mean())/(immax-immin)

        # Create Gaussian filter
        frames = imscaled.transpose(2, 1, 0) # conventional shaping

        if self.bandfilter == 0: #'Gaussian':
            sigma = np.floor(self.uc.dnscaled.bandwidth_pix/3)
            self.gauss1d = signal.gaussian(imsize, std=sigma)
            self.gauss2d = np.tile(self.gauss1d, (imsize, 1)) # Make it 2D
        elif self.bandfilter == 1: #'Square':
            sigma = np.floor(self.uc.dnscaled.bandwidth_pix)
            print 'dnscaled.bandwidth_pix', self.uc.dnscaled.bandwidth_pix
            self.gauss1d = np.zeros(imsize)
            self.gauss1d[
                int(imsize/2-sigma/2):int(imsize/2+sigma/2)
            ] = 1
            self.gauss2d = np.tile(self.gauss1d, (imsize, 1)) # Make it 2D

        if self.binary_threshold:
            thresh = np.percentile(frames, self.binary_threshold)
            frames[frames < thresh] = frames.min()
            frames[frames > thresh] = frames.max()

        # No need to have something like `gauss3d`. It is just overkill.
        # defines a period
        screenWidthDegEyePoint = np.arctan(
            (self.uc.width_cm * (1 - self.eyepoint_x)) / self.uc.distance_cm
        ) + np.arctan((self.uc.width_cm * self.eyepoint_x) / self.uc.distance_cm)

        frames_per_period = int(np.ceil(self.contr_period*self.framerate))
        self.theta = screenWidthDegEyePoint / frames_per_period
        self.space = np.linspace(0, nframes*self.theta, nframes)
        self.thetas = np.fmod(self.space, screenWidthDegEyePoint) - (screenWidthDegEyePoint * (1 - self.eyepoint_x))
        self.offsets = (imsize * self.uc.distance_cm * np.tan(self.thetas) / self.uc.width_cm) - imsize / 2
        # self.thetas = np.fmod(self.space, screenWidthDegEyePoint)
        # self.offsets = (imsize * self.uc.distance_cm * self.thetas / self.uc.width_cm)

        for frame, offset in zip(frames, self.offsets):
            frame[:] = (frame - 0.5) * np.roll(self.gauss2d, int(offset) - int(imsize*self.eyepoint_x))
        self.moviedata = cm.gray(frames + 0.5, bytes=True)
        self.shape = self.moviedata.shape # z, y, x
        return self.moviedata
    def viewmask(self):
        if not self.viewwidth:
            return
        ratio = ((self.uc.width_deg - self.viewwidth) / self.uc.width_deg * 100) / 2
        boundindex =  self.moviedata.shape[2] * (ratio/100)
        self.moviedata[:, :, -boundindex:] = 128
        self.moviedata[:, :, :boundindex] = 128
        return self
    def generate(self):
        self.stim_to_movie()
        return self
    def crop(self):
        amount = self.imsize - int(self.imsize*self.screenRatio)
        if self.rotation in [0, 2]:
            self.moviedata = self.moviedata[:, :, amount:]
        else:
            self.moviedata = self.moviedata[:, amount:, :]
        return self
    def rotate(self, direction=None):
        #   0: top to bottom
        # 180: bottom to top
        #  90: right to left
        # 270: left to right
        arr = self.moviedata
        computed = {0:3, 1:2, 2:1, 3:0}.get(direction or self.rotation)
        for index, frame in enumerate(arr):
            arr[index] = np.rot90(frame, computed)
        return self
    def stim_to_file(self):
        import tifffile
        if self.moviedata is None:
            self.moviedata = self.stim_to_movie()
        tifffile.imsave('/Volumes/Users/ht/Desktop/gaussianNoise.tif', self.moviedata)
        # tifffile.imsave('gaussianNoise.tif', movie)
        return self
def tempsave(data):
    import tifffile
    tifffile.imsave('/Volumes/Users/ht/Desktop/gaussianNoise.tif', data)
def test(**kwargs):
    qwe = SweepingNoiseGenerator(
            eyepoint_x = 0,
            duration=10, screenDistanceCm=5, rotation=1, bandwidth=30, **kwargs)
    qwe.generate()
    qwe.rotate()
    qwe.viewmask()
    # qwe.crop()
    tempsave(qwe.moviedata)
    return qwe
def test2(use_random=False):
    return SweepingNoiseGenerator(
        max_spat_freq = 0.05,
        max_temp_freq = 4,
        duration = 15,
        bandwidth = 30,
        screenDistanceCm = 10,
        rotation = 1,
        bandfilter = 1
        # viewwidth=20,
    ).generate().rotate() # .viewmask()
def test3():
    return SweepingNoiseGenerator(
        max_spat_freq = 0.5,
        max_temp_freq = 4,
        contrast = 0.5,
        rotation = 0,
        bandfilter = 0, # is gaussian
        duration = 3,
        bandwidth = 10,
        viewwidth = 0,
        framerate = 30,
        contr_period = 10,
        imsize = 128,
        screenWidthCm = 68.58,
        screenHeightCm = 121.92,
        screenWidthPix = 1080,
        screenHeightPix = 1920,
        viewport_x = 1080,
        viewport_y = 1920,
        screenDistanceCm = 25,
        eyepoint_x = 0.5,
        use_random = True,
    ).generate().rotate().viewmask()
# get_ipython().magic('pylab')
# qwe = test()
