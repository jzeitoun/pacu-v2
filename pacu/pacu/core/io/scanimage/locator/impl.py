import itertools

from pacu.util.prop.memoized import memoized_property

class CursoredList(list):
    _cursor = 0
    @classmethod
    def with_cursor(cls, iterable, cursor=0):
        # TODO: rename with->from_iterable_with_cursor?
        self = cls(iterable)
        self.cursor = cursor
        return self
    def __repr__(self):
        literal = super(CursoredList, self).__repr__()
        return '{}.with_cursor({}, {})'.format(
            type(self).__name__, literal, self.cursor)
    @property
    def cursor(self):
        return self._cursor
    @cursor.setter
    def cursor(self, val):
        if val >= len(self):
            raise IndexError('Can not have such an index `{}`.'.format(val))
        self._cursor = val
    def set_cursor(self, cursor):
        self.cursor = cursor
        return self
    def set_cursor_by_item(self, item):
        self.cursor = self.index(item)
        return self
    @property
    def current(self):
        return self[self.cursor]
    @property
    def couple(self):
        return self.cursor, self.current
    def loop(self):
        for index, element in enumerate(self):
            self.cursor = index
            yield element

class Locator(object):
    def __init__(self, sequence, sfrequencies, tfrequencies, orientations,
            blank=False, flicker=False):
        self.sequence = sequence
        self.unique_sequence = list(sorted(set(self.sequence)))
        self.sfrequencies = CursoredList.with_cursor(sfrequencies, 0)
        self.tfrequencies = CursoredList.with_cursor(tfrequencies, 0)
        self.orientations = CursoredList.with_cursor(orientations, 0)
        self.blank = blank
        self.flicker = flicker
    @classmethod
    def from_one_based_sequence(cls, seq, *args, **kwargs):
        return cls([s-1 for s in seq], *args, **kwargs)
    @memoized_property
    def condition_product(self):
        return list(itertools.product(self.orientations,
            self.tfrequencies, self.sfrequencies))
        # return list(itertools.product(self.sfrequencies,
        #     self.tfrequencies, self.orientations))
    @property
    def current_condition_index(self):
        return self.condition_product.index(
            self.current_condition_combination)
    @property
    def blank_condition_index(self):
        if self.blank:
            return len(self.condition_product)
    @property
    def flicker_condition_index(self):
        if self.flicker:
            return len(self.condition_product) + int(self.blank)
    @property
    def current_condition_combination(self):
        return (
            self.orientations.current,
            self.tfrequencies.current,
            self.sfrequencies.current)
        # return (
        #     self.sfrequencies.current,
        #     self.tfrequencies.current,
        #     self.orientations.current)
    @property
    def arg_condition_indice(self):
        """
        Returns a list like that current conditions repeatedly
        happened `nth` occurrence of it in actual order.
        Can be overridden by blank and flicker.
        """
        if self.blank_on:
            return self.arg_blank_indice
        elif self.flicker_on:
            return self.arg_flicker_indice
        else:
            return [arg for arg, seq in enumerate(self.sequence)
            if seq == self.current_condition_index]
    @property
    def arg_blank_indice(self):
        return [arg for arg, seq in enumerate(self.sequence)
            if seq == self.blank_condition_index]
    @property
    def arg_flicker_indice(self):
        return [arg for arg, seq in enumerate(self.sequence)
            if seq == self.flicker_condition_index]
    def map_condition_indice_from(self, array):
        return [array[index] for index in self.arg_condition_indice]
    def map_blank_indice_from(self, array):
        return [array[index] for index in self.arg_blank_indice]
    def map_flicker_indice_from(self, array):
        return [array[index] for index in self.arg_flicker_indice]
    @property
    def total_conditions(self):
        return len(self.condition_product) + int(self.blank) + int(self.flicker)
    @property
    def arg_last_sequence(self):
        return max(arg for arg, seq in enumerate(self.sequence)
            if seq == max(self.sequence))
    flicker_on = False
    blank_on = False
    def override_blank(self, on):
        self.blank_on = on
        self.flicker_on = False
        return True if on and self.blank else False
    def override_flicker(self, on):
        self.blank_on = False
        self.flicker_on = on
        return True if on and self.flicker else False
    def override(self, blank=False, flicker=False):
        self.blank_on = blank
        self.flicker_on = flicker
        return self
# nreps is 4
# nconds is 13
# blank = True
# flicker = False
# sfrs = [0.04]
# tfrs = [1]
# oris = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
# seq = [9,5,12,11,8,7,13,6,3,4,2,1,10,8,11,4,13,2,12,6,7,3,10,9,1,5,6,10,4,5,
#     2,3,1,13,8,12,11,7,9,5,4,2,13,11,10,1,9,7,8,3,6,12]
# l = Locator.from_one_based_sequence(seq, sfrs, tfrs, oris, blank, flicker)
# a = [l.arg_condition_indice for _ in l.orientations.loop()]
