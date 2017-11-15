import ujson as json
from pacu.profile import manager
from pacu.core.model.ed.visstim2p import VisStim2P
from pacu.core.model.experiment import ExperimentV1

DB = manager.get('db').as_resolved
ED = manager.get('db').section('ed')
LIMIT = 1000

def get(req, condtype):
    if condtype == '0': # ScanImage with Matlab VisStim
        ed = ED()
        models = ed.query(
            VisStim2P.id,
            VisStim2P.mouse_id,
            VisStim2P.filename,
            VisStim2P.spatial_frequencies,
            VisStim2P.total_time_S,
            VisStim2P.date
        ).order_by(VisStim2P.id.desc())[:LIMIT]
        return json.dumps([m._asdict() for m in models])
    else: # ScanBox with PACU VisStim
        db = DB()
        models = db.query(ExperimentV1
        ).order_by(ExperimentV1.id.desc())[:LIMIT]
        rv = []
        for m in models:
            rv.append(dict(
                id = m.id,
                filename = m.payload['handler']['kwargs']['exp_note'],
                spatial_frequencies = m.payload['stimulus']['kwargs'].get('sfrequencies')
            ))
        return json.dumps(rv)
