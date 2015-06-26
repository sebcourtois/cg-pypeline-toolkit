

from pytk.util.sysutils import toStr
from pytk.util.external.pathlib import Path

def toPath(p):

    if not p or isinstance(p, Path):
        return p
    else:
        return Path(toStr(p))