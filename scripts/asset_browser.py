
import sys

from PySide import QtGui

from pytk.davos.core.drctypes import DrcRepository
from pytk.davos.gui.assetbrowserwidget import AssetBrowserWidget
#from pytk.core.itemviews.basetreeview import BaseTreeView

if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)

    #print QtGui.QStyleFactory.keys()
    app.setStyle("Cleanlooks")

    view = AssetBrowserWidget()

    drcLib = DrcRepository("testlib", r"\\Diskstation\z2k\05_3D\zombillenium")

    view.loadModelData(drcLib)
    view.show()

    sys.exit(app.exec_())
