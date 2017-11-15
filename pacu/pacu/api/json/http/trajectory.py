from pacu.profile import manager
from pacu.core.io.trajectory.impl import TrajectoryIO

opt = manager.instance('opt')

def index_trial(recording):
    trial_paths = sorted(
        set(path
        for path in opt.trajectory_root.joinpath(recording).ls('*.tif')
        if path.is_file()))
    trials = map(TrajectoryIO, trial_paths)
    return dict(recording=recording, trials=[t.as_record for t in trials])

def index_record():
    recordings = sorted(set(path.name
        for path in opt.trajectory_root.ls()
        if path.is_dir() and len(path.ls('*.tif'))))
    return dict(recordings=recordings)

def get_index(req, recording=None):
    return index_trial (recording) if recording else \
           index_record()

def post_session(req, path, session):
    rec = TrajectoryIO(path)
    rec.set_session(session).session.create()
    return rec

def delete_session(req, path, session):
    rec = TrajectoryIO(path)
    rec.set_session(session).session.remove()
    return rec
