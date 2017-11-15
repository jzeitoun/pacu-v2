from pacu.core.model import ExperimentV1
from pacu.core.model.glams import Mice
from pacu.core.model.interim.impl import Interim
from pacu.core.model.interim.impl import engine as interim
from pacu.profile import manager
from pacu.ext.sqlalchemy.orm import session

orm_resource = dict(
    mice = [Mice, manager.get('db').section('glams'),
        lambda M, query, keyword: query.filter(M.name.contains(keyword)).filter(M.DOD == None).order_by(M.id.desc())
    ],
    scanbox_data = [Interim, lambda: interim,
        lambda M, query, keyword: query.filter(M.name.contains(keyword)).filter(M.type == 'scanbox_data').order_by(M.id.desc())
    ],
    experiment_v1 = [ExperimentV1, manager.get('db').instance,
        lambda M, query, keyword: query.filter(M.experiment_note.contains(keyword)).order_by(M.id.desc())
    ],
)

def to_sui_search(models, upto, count):
    if upto < count:
        footer = 'First {} of {} item(s)'.format(upto, count)
    else:
        footer = '{} item(s) found'.format(count)
    return dict(
        results = list(map(dict, models)),
        meta = dict(
            footer = footer
        )
    )
def make_query(Model, engine, flambda, keyword, upto):
    s = session.get_scoped(engine())
    query = s.query(Model)
    if keyword:
        query = flambda(Model, query, keyword)
    return [model.serialize() for model in query[:upto]], query.count()

def get(req, orm, keyword=None, upto=5):
    models, count = make_query(*orm_resource.get(orm), keyword=keyword, upto=upto)
    return to_sui_search(models, upto, count)

# models, count = make_query(*orm_resource.get('mice'), keyword='x', upto=5)
# models, count = make_query(*orm_resource.get('scanbox_data'), keyword='', upto=5)
# models, count = make_query(*orm_resource.get('experiment_v1'), keyword='', upto=5)
# models, count = make_query(Interim, interim, 'x', 5)
# result = to_sui_search(models, 5, count)
