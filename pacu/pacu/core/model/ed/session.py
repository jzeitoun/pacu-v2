from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from ext.model import dburi
from ext import console

engine = create_engine(dburi, echo=console.on)
Session = sessionmaker(bind=engine)
inspector = inspect(engine)
s = Session()
