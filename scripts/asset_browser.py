
import sys

from PySide import QtGui

# from pytk.davos.core.drclibrary import DrcLibrary
from pytk.davos.core.damproject import DamProject

from pytk.davos.gui.assetbrowserwidget import AssetBrowserWidget
# from pytk.core.itemviews.basetreeview import BaseTreeView



if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)

    # print QtGui.QStyleFactory.keys()
    app.setStyle("Cleanlooks")

    view = AssetBrowserWidget()

    proj = DamProject("zombillenium")

    proj.init()

    view.setupModelData(proj)
    view.show()

    proj.loadLibraries()

    sys.exit(app.exec_())
