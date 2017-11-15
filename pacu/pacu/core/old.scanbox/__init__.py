from pacu.core.scanbox.desc.mat import MatDescriptor
from pacu.core.scanbox.desc.path import PathDescriptor

class FileGroup(object): # sbx, mat and friends...
    def __init__(self, route):
        self.path = route # without extension
    path = PathDescriptor()
    mat = MatDescriptor().bind(path)
# from pacu.core.scanbox.mapper.mat import MatMapper
# jz5 = '/Volumes/Users/ht/tmp/pysbx-data/JZ5/JZ5_000_003'
# kj = '/Volumes/Users/ht/tmp/pysbx-data/KJ13.2_000_000'
# f = FileGroup(jz5)
# f = FileGroup(kj)
