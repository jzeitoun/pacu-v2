from __future__ import division

import numpy as np

from collections import namedtuple

class ExternalDivision(object):
    polygon = None
    distance = None
    centroid = None
    Point = namedtuple('Point', 'x y')
    def __init__(self, polygon):
        self.polygon = polygon
        self.centroid = self.get_centroid(polygon)
        self.distance = self.get_euclidean_distance(self.centroid, self.polygon)
    def get_euclidean_distance(self, ptrs_a, ptrs_b):
        phat, chat = (ptrs_a - ptrs_b).T
        return np.hypot(phat, chat)
    def get_centroid(self, polygon):
        closed = np.array(list(polygon) + [polygon[0]])
        pointXs = closed[:, 0]
        pointYs = closed[:, 1]

        areadiff = (pointXs[:-1] * pointYs[1:]) - (pointYs[:-1] * pointXs[1:])
        area = np.sum(areadiff) / 2.

        cx = pointXs[:-1] + pointXs[1:]
        cy = pointYs[:-1] + pointYs[1:]

        center_x = np.sum(cx * (areadiff)) / (6. * area)
        center_y = np.sum(cy * (areadiff)) / (6. * area)
        return self.Point(center_x, center_y)
    def get_3rd_points_by(self, further):
        total_distance = self.distance + further
        pointXs = (total_distance*self.polygon[:,0] - (further*self.centroid.x)
                  ) / self.distance
        pointYs = (total_distance*self.polygon[:,1] - (further*self.centroid.y)
                  ) / self.distance
        return np.vstack((pointXs, pointYs)).T
    def get_3rd_points_by_ratio(self, m, n):

        pointXs = (m*self.polygon[:,0] - n*self.centroid.x) / (m - n)
        pointYs = (m*self.polygon[:,1] - n*self.centroid.y) / (m - n)

        return np.vstack((pointXs, pointYs)).T
