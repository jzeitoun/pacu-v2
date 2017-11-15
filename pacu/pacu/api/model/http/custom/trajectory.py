from pacu.util.path import Path

class Session(object):
    def __init__(self, id, path):
        self.id = id
        self.path = path
    @property
    def hasimported(self):
        return len(self.path.ls('*.imported')) == self.number_of_trials
    @property
    def number_of_trials(self):
        return len(self.path.ls('*.tif'))
    @property
    def as_json(self):
        return dict(
            type='tr-session',
            id=self.id,
            attributes=dict(
                name=self.path.name,
                numberoftrials=self.number_of_trials,
                hasimported=self.hasimported,
        ))

# test = Path('/Volumes/Gandhi Lab - HT/Soyun/2016-02-04T14-27-00')
test = Path('/Volumes/Gandhi Lab - HT/Soyun/2016-02-11T09-56-35')
t = Session(0, test)
