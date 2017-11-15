def get(Model=None):
    if not Model:
        from .member import Member as Model
    return dict(
        sunil = Model(fullname=u'Sunil Gandhi'),
        hyungtae = Model(fullname=u'Hyungtae Kim'),
        melissa = Model(fullname=u'Melissa Davis'),
        dario = Model(fullname=u'Dario Figueroa'),
    )
def dump(session):
    session.add_all(get().values())
    session.commit()
