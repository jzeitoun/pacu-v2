class FSSerialization(object):
    fields = 'classes value name text icon'.split()
    def __init__(self, items):
        self.items = items
    def __iter__(self):
        return (
            {key: getattr(item, key) for key in self.fields}
            for item in self.items
        )
