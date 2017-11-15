from pacu.core.io.scanbox.model.variant.type import VariantBaseType
from pacu.core.io.scanbox.model.variant.type import Variant

class VTOriMeansParams(VariantBaseType):
    meantrace = Variant({})
    # indices = Column(PickleType, default={})
    # matrix = Column(PickleType, default=[])
    # meantrace = Column(PickleType, default=[])
    # on_frames = Column(Integer)
    # bs_frames = Column(Integer)
