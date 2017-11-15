from pacu.util.newtype.incremental_hash import IncrementalHash

class AbstractMeta(object):
    def __init__(self, feat, inst, attr):
        self.feature = feat.feature
        self.handle = inst.handle
        self.attr = attr
        self.inst = inst
    def coerce(self, value):
        coerced = self.coercer(value)
        setattr(self.inst, self.attr, coerced)
        return coerced
    def coercer(self, value):
        return value
    @property
    def current(self):
        return getattr(self.inst, self.attr)
    @property
    def implemented(self):
        return bool(self.handle.is_implemented(self.feature))
    @property
    def readonly(self):
        return bool(self.handle.is_readonly(self.feature))
    @property
    def readable(self):
        return bool(self.handle.is_readable(self.feature))
    @property
    def writable(self):
        return bool(self.handle.is_writable(self.feature))
    @property
    def max_int(self):
        return self.handle.get_int_max(self.feature)
    @property
    def min_int(self):
        return self.handle.get_int_min(self.feature)
    @property
    def max_float(self):
        return self.handle.get_float_max(self.feature)
    @property
    def min_float(self):
        return self.handle.get_float_min(self.feature)
    @property
    def max_string_length(self):
        return self.handle.get_string_max_length(self.feature)
    @property
    def enums(self):
        return list(self.handle.get_enums(self.feature))
    @property
    def range(self):
        raise NotImplementedError
    def __str__(self):
        return self.format_show()
    def show(self):
        print self.format_show()
    def export(self):
        return dict(
            feature     = self.feature,
            type        = type(self).__name__,
            key         = self.attr,
            value       = self.current,
            implemented = self.implemented,
            readonly    = self.readonly,
            readable    = self.readable,
            writable    = self.writable,
            range       = self.range,
        )
    def format_show(self):
        info = '{} - {} - {}'.format(
            self.feature, type(self).__name__, self.current)
        return '\n'.join([
            '-' * len(info),
            info,
            '-' * len(info),
            'Implemented: %s' % self.implemented,
            'Readonly   : %s' % self.readonly,
            'Readable   : %s' % self.readable,
            'Writable   : %s' % self.writable,
            'Range      : %s' % str(self.range),
        ])
class BaseFeature(IncrementalHash):
    Meta = AbstractMeta
    def __init__(self, feature):
        self.feature = feature
    def get_meta(self, inst, attr):
        return self.Meta(self, inst, attr)
