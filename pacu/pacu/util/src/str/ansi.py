class ansimorphicStr(str):
    @property
    def plain(self):
        return self
    @property
    def red(self):
        return '\033[91m%s\033[0m' % self
    @property
    def green(self):
        return '\033[92m%s\033[0m' % self
    @property
    def yellow(self):
        return '\033[93m%s\033[0m' % self
    @property
    def blue(self):
        return '\033[94m%s\033[0m' % self
    @property
    def megenta(self):
        return '\033[95m%s\033[0m' % self
    @property
    def cyan(self):
        return '\033[96m%s\033[0m' % self
    def __getitem__(self, key):
        return getattr(self, key or 'plain') if isinstance(key, str
            ) else super(ansimorphicStr, self).__getitem__(key)
