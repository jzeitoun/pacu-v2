from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

def get_scoped(engine):
    return scoped_session(sessionmaker(bind=engine))
