# encoding: utf8

class ROIs(list):
    error = None
    def __init__(self, iterable=None):
        super(ROIs, self).__init__(iterable or [])
    #     if isinstance(mmap, memmap):
    #         self.mmap = mmap
    #     else:
    #         self.error = TypeError(mmap)
    def append_roi(self, *args, **kwargs):
        pass
    def append_named_roi(self, name, *args, **kwargs):
        pass
q = ROIs()
# 이니셜허게 들어가는게 있고
# 피클에서 추출되는게 있고
# 네임드로 접근
# 인덱스로 접근
# 인벨리데이션
# rois 자체는 에러가없어야되고

