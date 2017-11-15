from pacu.util.descriptor.mixin.memoization import BindingMix
from pacu.core.scanbox.mapper.mat import MatMapper

class MatDescriptor(BindingMix):
    def __by_func__(self, value):
        try:
            return MatMapper(value)
        except IOError as e: # no file in there...
            return MatMapper.with_error(e)
        except TypeError as e: # probably not a mat file
            return MatMapper.with_error(e)
        except AttributeError as e: # value could be a non-path type
            return MatMapper.with_error(e)
