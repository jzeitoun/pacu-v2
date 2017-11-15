from __future__ import division

import numpy as np

def get_bandwidth(distance, deg):
    # to get opposite with `distance` as adjacent deg as `theta`
    return np.tan(np.deg2rad(deg))*distance

class SubUnit(object):
    def __init__(self, uc):
        self.uc = uc

class UnitConverter(object):
    def __init__(self,
            width_pix, height_pix,
            width_cm, height_cm,
            distance_cm, bandwidth_deg,
            image_size, direction,
            view_x=None, view_y=None):
        #direction 1 for azimuth (moving horizontally)
        self.width_pix = width_pix
        self.height_pix = height_pix
        self.width_cm = width_cm
        self.height_cm = height_cm
        self.distance_cm = distance_cm
        self.bandwidth_deg = bandwidth_deg
        self.image_size = image_size
        self.direction = direction
        self.view_x = view_x or width_pix
        self.view_y = view_y or height_pix
        self.x_ratio = self.view_x / self.width_pix
        self.y_ratio = self.view_y / self.height_pix
    # relatively static
    @property
    def width_deg(self):
        return 2*np.rad2deg(np.arctan(
            (0.5*self.width_cm)/self.distance_cm))
    @property
    def height_deg(self):
        return 2*np.rad2deg(np.arctan(
            (0.5*self.height_cm)/self.distance_cm))
    @property
    def bandwidth_cm(self):
        return get_bandwidth(self.distance_cm, self.bandwidth_deg)
    @property
    class upscaled(SubUnit):
        @property
        def deg_per_pix(self):
           return self.uc.deg_per_pix*self.uc.image_mag
    @property
    class dnscaled(SubUnit):
        @property
        def bandwidth_pix(self):
           return (self.uc.bandwidth_cm/self.uc.image_mag)*self.uc.pix_per_cm
    # relatively dynamic
    @property
    def image_mag(self):
        return self.axis.pix/self.image_size
    @property
    def deg_per_pix(self):
        return self.axis.deg/self.axis.pix
    @property
    def pix_per_cm(self):
        return self.axis.pix/self.axis.cm
    @property
    def bandwidth_pix(self):
        return (self.axis.pix/self.axis.deg)*self.bandwidth_deg
    @property
    class axis(SubUnit):
        @property
        def as_name(self):
            return 'Azimuth' if self.uc.direction else 'Elevation'
        @property
        def view_ratio(self):
            return self.uc.x_ratio if self.uc.direction else self.uc.y_ratio
        @property
        def pix(self):
            return (self.uc.width_pix if self.uc.direction else self.uc.height_pix)*self.view_ratio
        @property
        def deg(self):
            return (self.uc.width_deg if self.uc.direction else self.uc.height_deg)*self.view_ratio
        @property
        def cm(self):
            return (self.uc.width_cm if self.uc.direction else self.uc.height_cm)*self.view_ratio

    def show(self):
        uc = self
        print 'axis', uc.axis.as_name
        print 'axis deg', uc.axis.deg
        print 'axis cm', uc.axis.cm
        print 'axis pix', uc.axis.pix
        print 'axis view ratio xy', uc.axis.view_ratio
        print 'viewport xy', uc.view_x, uc.view_y
        print 'bandwidth deg', uc.bandwidth_deg
        print 'bandwidth cm', uc.bandwidth_cm
        print 'bandwidth pix', uc.bandwidth_pix
        print 'down scaled bandwidth pix', uc.dnscaled.bandwidth_pix
        print 'width deg', uc.width_deg
        print 'width cm', uc.width_cm
        print 'width pix', uc.width_pix
        print 'height deg', uc.height_deg
        print 'height cm', uc.height_cm
        print 'height pix', uc.height_pix
        print 'image mag', uc.image_mag
        print 'upscaled deg per pix', uc.upscaled.deg_per_pix

def test():
    print '==============================='
    uc1 = UnitConverter(1440, 900, 33.169, 20.731, 10, 10, 64, 1)
    uc1.show()
    print '==============================='
    uc2 = UnitConverter(1440, 900, 33.169, 20.731, 10, 30, 64, 1, view_x=900)
    uc2.show()
    print '==============================='
    uc3 = UnitConverter(1920, 1080, 53, 30, 10, 30, 64, 1)
    uc3.show()
    print '==============================='
    uc3 = UnitConverter(1080, 1920, 68.58, 121.92, 10, 30, 64, 1)
    uc3.show()
    return uc1, uc2, uc3
