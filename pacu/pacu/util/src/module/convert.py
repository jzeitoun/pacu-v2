def to_dict(module):
    return {key: val for key, val in vars(module).items()
            if not key.startswith('_')}
