# one = dict(
#     type=u'i3d',
#     title=u'First transplantation',
#     user=u'Sunil',
#     desc=u'The brain has the remarkable capacity to rewire its connections and thereby reorganize its function. In the juvenile brain, the plasticity of neuronal connections mediates the fine-tuning of a wide range of behaviors, from visual perception to language acquisition to social recognition.',
#     host=u'Scanbox',
#     src=u'JZ_003'
# )
# two = dict(
#     type=u'i3d',
#     title=u'The dummy session',
#     user=u'HT',
#     desc=u'What mechanism regulates the plasticity of connections in the young brain? How might we manipulate neural circuits to reactivate this plasticity?',
#     host=u'Scanbox',
#     src=u'JZ_006'
# )
def get(Model=None):
    if not Model:
        from .analysis import AnalysisV1 as Model
    return dict(
        # one = Model(**one),
        # two = Model(**two),
    )
def dump(session):
    session.add_all(get().values())
    session.commit()
