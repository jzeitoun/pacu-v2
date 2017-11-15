from ..level import logging

class PlainFormatter(logging.Formatter):
    def format(self, record):
        record.name         = '%s'   % (record.name)
        record.delimiter    = '%s'   % ('@')
        record.levelinitial = '|%s|' % (record.levelname[0])
        record.location     = ('%s.%s:' % (record.filename[:-3], record.funcName)) if record.levelno > 5 else ''
        return super(PlainFormatter, self).format(record)
    def __init__(self, fmt=None, datefmt=None):
        summary  = '%H:%M:%S'
        detail   = '%Y-%m-%d ' + summary
        time_fmt = summary
        super(PlainFormatter, self).__init__(fmt, time_fmt)
plain_formatter = PlainFormatter(
    '%(name)s%(delimiter)s'
    '%(asctime)s%(levelinitial)s'
    '%(location)s'
    ' %(message)s '
)
