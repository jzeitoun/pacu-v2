from __future__ import print_function

from pacu.ext.sqlalchemy.orm import session
from pacu.core.model import Base
from ... import profile
from ...util.format.table import simple
from ...util.input.qna import QnA

DB = profile.manager.get('db')

def ask_table(name):
    print('Could not find any matching table with `{}`.'.format(name))
    tables = Base.metadata.tables.keys()
    candidates = [tname for tname in tables if name in tname]
    if not candidates:
        print('There is no matching table.', end='\n\n')
        return
    if len(candidates) == 1:
        name = candidates[0]
        print('Did you mean `{}`?'.format(name), end='\n\n')
        return name
    print('Found possible tables.')
    item_range = range(len(candidates))
    print('    ',
           *['(%s) %s' % (index+1, candy)
               for index, candy in enumerate(candidates)],
       sep='\n    ', end='\n\n')
    qna = QnA('Which one? (1-%d), others to quit: ' % len(candidates)).ask()
    ans = qna.answer
    if ans and ans.isdigit() and int(ans)-1 in item_range:
        print('')
        name = candidates[int(ans)-1]
        return name

def make_query(model, model_id=0):
    s = DB.instance()
    table = Base.metadata.tables[model]
    if model_id:
        data = s.query(table).filter_by(id=model_id).first()
        return data._asdict() if data else \
            'Could not find {} by id {}.'.format(model, model_id)
    else:
        data = s.query(table).all()
    return data if data else 'This table is empty.'

def main(model, model_id=0):
    if model:
        return make_query(model, model_id=model_id)
    else:
        table_names = sorted(Base.metadata.tables.keys())
        header = 'You can make a query for below tables.'
        return '\n    '.join([header] + table_names)

if __name__ == '__api_main__':
    if model and model not in Base.metadata.tables:
        model = ask_table(model)
    result = main(model, id)
    if isinstance(result, dict):
        print(simple.show(
            '{} #{}'.format(model, id), sorted(result.items())))
    else:
        print(result)
