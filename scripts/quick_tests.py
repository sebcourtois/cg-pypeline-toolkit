
import sys

from PySide import QtGui


from pytk.core.dialogs import loginDialog

qApp = QtGui.QApplication(sys.argv)

def checkLogin(sUser, sPwd):

    if sUser == "toto":
        return {"user":"toto"}

    return None

print loginDialog(loginFunc=checkLogin)

# from pytk.davos.core.damproject import DamProject
# proj = DamProject("zombillenium")
#
# print proj.getRcPath("public", "shot_lib")
# print proj.getRcPath("private", "shot_lib")
# print proj.getRcPath("public", "asset_lib", "texture_dir")
