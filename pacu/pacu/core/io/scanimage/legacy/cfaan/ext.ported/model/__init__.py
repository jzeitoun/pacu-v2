from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base

dburi = '{SCHEMA}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'.format(
    SCHEMA   = 'mysql',
    HOST     = '128.200.21.99',
    PORT     = '3306',
    USERNAME = 'gandhilab',
    PASSWORD = 'mge2cortex',
    DBNAME   = 'ed',
)

Base = declarative_base()

def PKColumn(*args, **kwargs):
    return Column(*args, primary_key=True, **kwargs)


