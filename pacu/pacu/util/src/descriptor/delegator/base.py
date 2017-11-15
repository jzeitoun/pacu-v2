class DelegatorBase(object):
    def __init__(self, proxy):
        self.proxy = proxy
    def __dir__(self):
        return self.proxy._attrs.keys()
    def __iter__(self):
        return iter(map(self.__getattr__, self.__dir__()))
    def __getattr__(self, key):
        return self(self.proxy._attrs, key)
    def __call__(self, attrs, key):
        pass
