from pathlib import Path
from pacu.util import identity
from pacu.util.str.poly import polymorphicStr

def warn_existence(key, path):
    print 'Path `{!s}` for `{}` does not exist.'.format(path, key)
def raise_existence(key, path):
    raise SystemExit('Path `{!s}` for `{}` does not exist.'.format(path, key))
def xform_with_path(profile, strict):
    pdict = {key: val.path for key, val in vars(profile).items()}
    for key, path in pdict.items():
        if not path.is_dir():
            warn_existence(key, path)
            cwd = Path.cwd()
            print 'replaced with', cwd
            setattr(profile, key, cwd)
            # raise_existence(key, path) if strict else warn_existence(key, path)
        else:
            setattr(profile, key, path.resolve())
    return profile
def default(profile):
    if not profile.scanbox_root:
        profile.scanbox_root = polymorphicStr(identity.path.cwd)
    if not profile.scanimage_root:
        profile.scanimage_root = polymorphicStr(identity.path.cwd)
    return xform_with_path(profile, True)
