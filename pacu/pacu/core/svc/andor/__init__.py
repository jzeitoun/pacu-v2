from pacu.core.svc.andor.fake import FakeAndorBindingService
from pacu.core.svc.andor.impl import AndorBindingService as RealAndorBindingService

class AndorBindingService(object):
    def __new__(cls, files=-1):
        Service = FakeAndorBindingService if files in ['fake', -1] \
             else RealAndorBindingService
        return Service(files)
