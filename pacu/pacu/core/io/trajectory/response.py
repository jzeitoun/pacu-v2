class TrajectoryResponse(object):
    def __init__(self, array):
        self.trace = array
        self.overview = dict(array=array)
