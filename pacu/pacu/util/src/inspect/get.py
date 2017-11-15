from collections import OrderedDict

def clsname(instance):
    return type(instance).__name__

def fumble_val_by_key(cls, key):
    try:
        mro = cls.mro()
    except TypeError: # metaclass support
        mro = cls.mro(cls)
    for c in mro:
        try:
            return c.__dict__[key]
        except:
            continue
    else:
        raise KeyError(key)

def fumble_key_by_val(inst, ref):
    cls = type(inst)
    try:
        mro = cls.mro()
    except TypeError: # metaclass support
        mro = cls.mro(cls)
    for c in mro:
        for key, val in vars(c).items():
            if val is ref:
                return key

def agg_public_types(nmspc, atype, orders=()):
    keys = orders or [k for k in dir(nmspc) if not k.startswith('_')]
    vals = [fumble_val_by_key(nmspc, key) for key in keys]
    kvs = [(k, v) for k, v in zip(keys, vals) if isinstance(v, atype)]
    return OrderedDict(
        kvs if orders else sorted(kvs, key=lambda item: hash(item[1]))
    )

