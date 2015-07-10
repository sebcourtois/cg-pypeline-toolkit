
import re
import os

from pytk.core.dialogs import promptDialog
from pytk.util.logutils import logMsg
from pytk.util.external.lockfile.mkdirlockfile import MkdirLockFile
from pytk.util.external.lockfile import LockError, UnlockError

_interDashesRgx = re.compile(r'-([a-z][0-9]+)')


class LockFile(MkdirLockFile):

    def __init__(self, path, sOwnerName):

        self.path = path
        root, tail = os.path.split(path)
        self.lock_file = os.path.join(os.path.abspath(root), "." + tail) + ".lock"
        self.unique_name = os.path.join(self.lock_file, sOwnerName)
        self.timeout = -1

    def owner(self):
        logMsg(log='all')

        if not self.is_locked():
            return ""

        files = os.listdir(self.lock_file)
        return files[0] if files else ""

    def set_locked(self, bLock):
        if bLock:
            try:self.acquire()
            except LockError:return False
        else:
            try:self.release()
            except UnlockError:return False

        return True

def findVersionFields(s):
    return _interDashesRgx.findall(s)

def formattedVersion(letter, version):
    return '{}{:03d}'.format(letter, version)

def addVersionSuffixes(sFileNameOrPath, *versions):

    sRootPath, sExt = os.path.splitext(sFileNameOrPath)

    sJoinList = [sRootPath]
    sJoinList.extend(versions)

    return "-".join(sJoinList) + sExt

def promptForComment(**kwargs):

    result = promptDialog(title='Please...',
                        message='Leave a comment: ',
                        button=['OK', 'Cancel'],
                        defaultButton='OK',
                        cancelButton='Cancel',
                        dismissString='Cancel',
                        scrollableField=True,
                        **kwargs)

    if result == 'Cancel':
        logMsg("Cancelled !" , warning=True)
        return

    sComment = promptDialog(query=True, text=True)
    if not sComment:
        return

    return sComment
