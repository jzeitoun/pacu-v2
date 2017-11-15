def is_degree_bound(self, value):
    if not 0.0 <= value <= 360.0:
        return 'The value %s of `%s` should be in range between 0.0 and 360.0' % (
            value, type(self).__name__)
def is_zpositive(self, value):
    if value < 0:
        return 'The value %s of `%s` should not be a negative number.' % (
            value, type(self).__name__)
def is_positive(self, value):
    if not value > 0:
        return 'The value %s of `%s` should be a positive number.' % (
            value, type(self).__name__)
