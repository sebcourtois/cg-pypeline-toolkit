
import re

from pytk.core.dialogs import promptDialog
from pytk.util.logutils import logMsg

_interDashesRgx = re.compile(r'-([^-]*?)-')

def findVersions(s):
    return _interDashesRgx.findall(s)

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
