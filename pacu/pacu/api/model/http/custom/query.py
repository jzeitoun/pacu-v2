import itertools

from pacu.util.path import Path
from pacu.api.model.http.custom.trajectory import Session

datapath = Path("/Volumes/Gandhi Lab - HT/Soyun")
test_path = Path('/Volumes/Gandhi Lab - HT/Soyun/2016-02-11T09-56-35')

def get_session_path(id):
    return sorted(datapath.ls('2016-*'))[id]

def list_session_paths():
    return enumerate(sorted(datapath.ls('2016-*')))

def trajectory_sessions(id=None):
    sessions = itertools.starmap(Session, list_session_paths())
    data = [session.as_json for session in sessions]
    return data[int(id)] if id else data
