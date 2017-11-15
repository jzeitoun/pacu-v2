import numpy as np
import cv2
from ext.util.calc.centroid import ExternalDivision
from ext.console import debug

class Neuropil(object):

    cells = None
    outers = None
    _pixels = None

    def __init__(self, cells, pixels):
        self.cells = cells
        self.pixels = pixels

    @property
    def pixels(self):
        return self._pixels

    @pixels.setter
    def pixels(self, val):
        self._pixels = val
        self.outers = [
            ExternalDivision(cell).get_3rd_points_by(self.pixels).round().astype(int)
            for cell in self.cells
        ]

    def get_others(self, nth):
        return [outer
            for index, outer in enumerate(self.outers) if index != nth]

    def get_masked_neuropil(self, shape, nth):
        main_outer_mask = np.zeros(shape, np.uint8)
        others_mask = np.zeros(shape, np.uint8)

        main_outer = self.outers[nth]
        cv2.drawContours(main_outer_mask, [main_outer], 0, 255, self.pixels)

        others = self.get_others(nth)
        for other in others:
            cv2.drawContours(others_mask, [other], 0, 255, self.pixels)

        main_outer = self.mask(main_outer_mask)
        others = self.mask(others_mask)

        intersaction = ~(main_outer.mask | others.mask)
        has_colllision = intersaction.any()
        main_outer.mask[intersaction] = True
        return main_outer, has_colllision

    def mask(self, array):
        return np.ma.masked_where(array == 0, array)

class RatioNeuropil(object):

    cells = None
    outers = None
    _option = None

    def __init__(self, cells, option):
        self.cells = cells
        self.option = option

    @property
    def option(self):
        return self._option

    @option.setter
    def option(self, val):
        self._option = val
        self.outers = [
            ExternalDivision(cell).get_3rd_points_by_ratio(
                self.option.m, self.option.n).round().astype(int)
            for cell in self.cells
        ]

    def get_others_outer(self, nth):
        return [outer
            for index, outer in enumerate(self.outers) if index != nth]
    def get_others_inner(self, nth):
        return [outer
            for index, outer in enumerate(self.cells) if index != nth]

    def get_neuropil_mask(self, shape, outer, inner):
        outer_mask = np.zeros(shape, np.uint8)
        inner_mask = np.zeros(shape, np.uint8)
        cv2.drawContours(outer_mask, [outer], 0, 255, -1)
        cv2.drawContours(inner_mask, [inner], 0, 255, -1)
        return outer_mask - inner_mask

    def get_single_neuropil(self, shape, nth):
        if not self.option.active:
            return np.zeros(shape, np.uint8)

        main_outer = self.outers[nth]
        main_inner = self.cells[nth]
        main_neuropil_mask = self.get_neuropil_mask(shape, main_outer, main_inner)

        return main_neuropil_mask

    def get_neuropil(self, shape, nth):
        if not self.option.active:
            return np.zeros(shape, np.uint8), False

        main_outer = self.outers[nth]
        main_inner = self.cells[nth]
        main_neuropil_mask = self.get_neuropil_mask(shape, main_outer, main_inner)
        original_np_sum = main_neuropil_mask.sum()

        others_outer = self.get_others_outer(nth)
        others_inner = self.get_others_inner(nth)

        for outer, inner in zip(others_outer, others_inner):
            other_neuropil_mask = self.get_neuropil_mask(shape, outer, inner)
            main_neuropil_mask[
                np.logical_and(main_neuropil_mask, other_neuropil_mask)
            ] = 0

        diffed_np_sum = main_neuropil_mask.sum()
        has_collision = original_np_sum != diffed_np_sum

        return main_neuropil_mask, has_collision

    def mask(self, array):
        return np.ma.masked_where(array == 0, array)

