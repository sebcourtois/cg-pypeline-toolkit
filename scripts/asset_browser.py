
import sys

from PySide import QtGui

from pytk.davos.core.drclibrary import DrcLibrary
from pytk.davos.gui.assetbrowserwidget import AssetBrowserWidget
#from pytk.core.itemviews.basetreeview import BaseTreeView

if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)

    #print QtGui.QStyleFactory.keys()
    app.setStyle("Cleanlooks")

    view = AssetBrowserWidget()

    drcLib = DrcLibrary("testlib", r"\\Diskstation\z2k\05_3D\zombillenium")

    view.setupModelData(drcLib)
    view.show()

    sys.exit(app.exec_())
