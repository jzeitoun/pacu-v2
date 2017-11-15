from ext.console import  debug

# Written by Hyungtae Kim <hyungtk@uci.edu>, in Nov 2014
# This enables the program to hold a specific spatial frequency
# to display a functional response.

class InvalidMetaError(Exception): pass
class InvalidCursorError(Exception): pass
class SpatialFrequencyMeta(object):
    def __init__(self, condition, sfreq_cursor=0, tfreq_cursor=0):
        self.condition = condition
        self.tfrequencies = condition['temporal_frequencies']
        self.sfrequencies = condition['spatial_frequencies']
        self.orientations = condition['orientations']
        # flickerOn was not counted, so in this case we deduct only blankOn parameter.
        self.n_conditions = condition['nConditions'] - int(condition['blankOn'])
        self.sfreq_cursor = sfreq_cursor
        self.tfreq_cursor = tfreq_cursor
        self.verify()

    def verify(self):
        if self.n_conditions != reduce(
                lambda n, y: n * len(y),
                [self.sfrequencies, self.orientations, self.tfrequencies],
                1
            ):
                raise InvalidMetaError(
                    'Logical relationship among some variables '
                    'in conditions seems not valid.'
                    'Total number of conditions should equal to '
                    '(a number of orientations) X (a number of spatial frequencies) X (a number of temporal frequencies).'
                    'The program may not work correctly.'
                    'Please notify Hyungtae Kim <hyungtk@uci.edu> to solve this issue.'
                    '(InvaildMetaError in `verify` at `model.sfreq_meta`)'
                )
    @property
    def has_blank(self):
        return bool(self.condition['blankOn'])
    @property
    def has_flicker(self):
        return bool(self.condition['flickerOn'])
    @property
    def blank_index(self):
        if self.has_blank:
            return self.n_conditions
    @property
    def flicker_index(self):
        if self.has_flicker:
            return self.n_conditions + int(self.has_blank)
    @property
    def sequence(self):
        return self.condition['sequence']
    @property
    def sfreq_cursor(self):
        return self._sfreq_cursor
    @property
    def tfreq_cursor(self):
        return self._tfreq_cursor
    @property
    def cur_sfreq(self):
        return self.sfrequencies[self.sfreq_cursor]
    @property
    def cur_tfreq(self):
        return self.tfrequencies[self.tfreq_cursor]

    @sfreq_cursor.setter
    def sfreq_cursor(self, value):
        if value not in range(len(self.sfrequencies)):
            raise InvalidCursorError(
                'Selected frequency is out of range.'
                'The program may not work correctly.'
                'Please notify Hyungtae Kim <hyungtk@uci.edu> to solve this issue.'
                '(InvaildCursor in `@sfreq_cursor` at `model.sfreq_meta`)'
            )
        self._sfreq_cursor = value

    @tfreq_cursor.setter
    def tfreq_cursor(self, value):
        if value not in range(len(self.tfrequencies)):
            raise InvalidCursorError(
                'Selected frequency is out of range.'
                'The program may not work correctly.'
                'Please notify Hyungtae Kim <hyungtk@uci.edu> to solve this issue.'
                '(InvaildCursor in `@sfreq_cursor` at `model.sfreq_meta`)'
            )
        self._tfreq_cursor = value

    @property
    def initial_index(self):
        return self.sfreq_cursor * len(self.tfrequencies) + self.tfreq_cursor

    @property
    def conditions_by_chunk(self):
        n_o = len(self.orientations)
        n_t = len(self.tfrequencies)
        n_s = len(self.sfrequencies)
        return range(self.initial_index, n_o*n_s*n_t, n_s*n_t)
        # start = len(self.orientations) * self.sfreq_cursor #* self.tfreq_cursor
        # stop = len(self.orientations) * (self.sfreq_cursor + 1) #* (self.tfreq_cursor + 1)
        # return range(start, stop)
    @property
    def conditions_and_orientations(self):
        conds = self.conditions_by_chunk
        return zip(conds, self.orientations)

    def make_analysis_data(self, response):
        if response.blank:
            return dict(
                hasblank = True,
                blank = [rep.trace.mean() for rep in response.blank.reps],
                oris = [[rep.trace.mean() for rep in ori.reps] for ori in response.orientations]
            )
        else:
            return dict(
                hasblank = False,
                blank = [],
                oris = [[rep.trace.mean() for rep in ori.reps] for ori in response.orientations]
            )

    def make_export_data(self, response):
        blank = (
            'blank', [rep.trace.mean() for rep in response.blank.reps]
        ) if response.blank else ()
        oris = [
            (ori.name, [rep.trace.mean() for rep in ori.reps])
            for ori in response.orientations
        ]
        return [blank] + oris
