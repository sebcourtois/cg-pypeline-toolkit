
from PySide import QtCore
from PySide import QtGui
Qt = QtCore.Qt

from pytk.core.itemviews.baseproxymodel import BaseProxyModel
from pytk.core.itemviews.basetreeview import BaseTreeView
from pytk.core.itemviews.basetreewidget import BaseTreeWidget
from pytk.core.itemviews.propertyitemmodel import PropertyItemModel
from pytk.core.itemviews.propertyitemmodel import PropertyIconProvider

from pytk.util.logutils import logMsg

from .childrenwidget import ChildrenWidget


class FileIconProvider(PropertyIconProvider):

    def __init__(self):
        super(FileIconProvider, self).__init__()
        self.__qprovider = QtGui.QFileIconProvider()

    def icon(self, metaprpty):
        fileInfo = metaprpty._metaobj._qfileinfo
        if fileInfo.isDir():
            return self.__qprovider.icon(QtGui.QFileIconProvider.Folder)
        return self.__qprovider.icon(fileInfo)

class DrcEntryModel(PropertyItemModel):

    iconProviderClass = FileIconProvider

class BrowserProxyModel(BaseProxyModel):

    def __init__(self, parent=None):
        super(BrowserProxyModel, self).__init__(parent)

    def filterAcceptsRow(self, srcRow, srcParentIndex):

        srcModel = self.sourceModel()
        parentItem = srcModel.itemFromIndex(srcParentIndex)
        if parentItem:
            childItem = parentItem.child(srcRow, srcParentIndex.column())
            return childItem.hasChildren()

        return BaseProxyModel.filterAcceptsRow(self, srcRow, srcParentIndex)

class BrowserTreeWidget(BaseTreeWidget):

    itemModelClass = DrcEntryModel
    proxyModelClass = BrowserProxyModel
    treeViewClass = BaseTreeView
#    contextMenuClass = ContextMenu

    def __init__(self, parent=None, childrenViewEnabled=True):
        super(BrowserTreeWidget, self).__init__(parent)

        self.treeView.mousePressEventButtons = (Qt.LeftButton,)

        #Create the childrenWidget
        self.childrenWidget = ChildrenWidget(self)

        #Create a widget named "switchWidget" to get the place of dataView in the splitter
        self.switchWidget = QtGui.QWidget(self.splitter)
        self.splitter.insertWidget(1, self.switchWidget)

        #Place dataView inside this new switchWidget
        self.dataView.setParent(self.switchWidget)

        #Create a layout for the switchWidget
        self.switchLayout = QtGui.QVBoxLayout(self.switchWidget)
        self.switchLayout.setSpacing(0)
        self.switchLayout.setContentsMargins(0, 0, 0, 0)
        self.switchLayout.setObjectName("switchLayout")

        self.switchLayout.addWidget(self.childrenWidget)
        self.switchLayout.addWidget(self.dataView)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.childrenViewEnabled = childrenViewEnabled
        if childrenViewEnabled:
            self.dataView.setVisible(False)
        else:
            self.childrenWidget.setVisible(False)

    def selectItems(self, *itemList , **kwargs):

        model = self.model()

        indexes = tuple(model.indexForItem(item) for item in itemList if (item != model.invisibleRootItem()))

        self.treeView.selectIndex(*indexes, **kwargs)

    def setupModelData(self, metamodel, **kwargs):

#        bUsePrxMdl = kwargs.get("useProxyModel", True)
#        kwargs["useProxyModel"] = bUsePrxMdl

        self.disconnectChildrenWidget()

        BaseTreeWidget.setupModelData(self, metamodel, **kwargs)

        self.resizeColumnsToContents()

#        self.setUiCategory("ZZ_Dev" if cmnCfg.isDevEnabled() else 0)

        self.childrenWidget.setModel(self.model())

        self.treeView.clicked.connect(self.childrenWidget.selectionModel().clear)

        self.setChildrenWidgetVisible(self.childrenViewEnabled)

    def syncTreeSelection(self, index):

        bItemPressed = self.treeView.wasAnItemPressed()
        logMsg("syncTreeSelection, treeView item pressed = {0}".format(bItemPressed), log='debug')
        if not bItemPressed:
            self.treeView.selectIndex(index)

    def disconnectChildrenWidget(self):

        childrenWidget = self.childrenWidget
        childrenView = self.childrenWidget.childrenView
        treeView = self.treeView

        selModel = self.selectionModel()
        if selModel:
            try: selModel.currentChanged.disconnect(childrenWidget.changeRootIndex)
            except RuntimeError: pass
            try: selModel.currentRowChanged.disconnect(childrenWidget.updatePathBar)
            except RuntimeError: pass

        try: treeView.clicked.disconnect(childrenWidget.changeRootIndex)
        except RuntimeError: pass

        try: childrenView.rootIndexChanged.disconnect(self.syncTreeSelection)
        except RuntimeError: pass

        try: childrenView.rootIndexChanged.disconnect(childrenWidget.updatePathBar)
        except RuntimeError: pass

    def connectChildrenWidget(self):

        childrenWidget = self.childrenWidget
        childrenView = self.childrenWidget.childrenView
        treeView = self.treeView

        selModel = self.selectionModel()

        curIndex = selModel.currentIndex()
        if curIndex.isValid():
            childrenWidget.changeRootIndex(curIndex)

        selModel.currentChanged.connect(childrenWidget.changeRootIndex)
        treeView.clicked.connect(childrenWidget.changeRootIndex)
        childrenView.rootIndexChanged.connect(self.syncTreeSelection)
        selModel.currentRowChanged.connect(childrenWidget.updatePathBar)
        childrenView.rootIndexChanged.connect(childrenWidget.updatePathBar)

    def setChildrenWidgetVisible(self, bVisible):

        childrenWidget = self.childrenWidget
        childrenView = self.childrenWidget.childrenView
        treeView = self.treeView

        if bVisible:
            treeView.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.connectChildrenWidget()
        else:
            treeView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.dataView.setVisible(not bVisible)
        childrenWidget.setVisible(bVisible)

        childrenWidget.updatePathBar(childrenView.rootIndex())
        treeView.updateGeometries()

        return

    def switchViews(self):
        self.setChildrenWidgetVisible((not self.childrenWidget.isVisible()))


    def revealLeaf(self, leaf, **kwargs):

        parentList = leaf.getAllParents()
        parentList.reverse()

#        for p in parentList:
#            p.updateLeaf( emitLeafAdded = False )

        treeView = self.treeView
        childrenWdg = self.childrenWidget
        bChildrenWdgVis = childrenWdg.isVisible()

#        for p in parentList:
#            self.treeView.loadLeafChildren( p )

        model = self.model()

        for par in parentList:
            index = model.indexForLeaf(par)
            if index.isValid() and not treeView.isExpanded(index):
                if bChildrenWdgVis:
                    childrenWdg.changeRootIndex(index)
                else:
                    treeView.setExpanded(index, True)

        if bChildrenWdgVis:
            if parentList:
                self.selectLeaf(par)
            childrenWdg.revealLeaf(leaf, **kwargs)
        else:
            self.selectLeaf(leaf)
