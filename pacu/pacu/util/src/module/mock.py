import types

suffix = '.mock.MockModule'

class MockModule(types.ModuleType):
    def __init__(self, name=None):
        name = name or (__package__ + suffix)
        super(MockModule, self).__init__(name)
