
from PySide import QtGui
from PySide.QtCore import Qt

from pytk.util.sysutils import toUnicode
from pytk.util.strutils import labelify
from pytk.util.qtutils import setWaitCursor

from pytk.core.metaproperty import EditState as Eds

from .utils import ItemUserFlag
from .utils import ItemUserRole
from .utils import toDisplayText

class PropertyItem(QtGui.QStandardItem):

    def __init__(self, metaprpty=None):
        super(PropertyItem, self).__init__()

        self.childrenLoaded = False

        self._metaprpty = metaprpty
        if metaprpty:
            self.__metaobj = metaprpty._metaobj

        self.setFlags(Qt.ItemFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable))

    def type(self):
        return QtGui.QStandardItem.UserType + 1

    def isValid(self):
        return (self._metaprpty is not None)

    def loadData(self, metaprpty):

        self.__metaobj = metaprpty._metaobj

        self.setData(toDisplayText(metaprpty.getattr_()), Qt.DisplayRole)
        self.setData(getattr(self.__metaobj.__class__, "classUiPriority", 0), ItemUserRole.SortGroupRole)

        if metaprpty.getParam("uiDecorated", False):
            icon = self.model().iconProvider().icon(toUnicode(self.__metaobj._pathobj))
            #icon = self.model().iconProvider().icon(QtGui.QFileIconProvider.Folder)
            self.setIcon(icon)

        self.loadFlags(metaprpty)

    def loadFlags(self, metaprpty):

        itemFlags = self.flags()
        editableState = metaprpty.getParam("uiEditable", Eds.Disabled)
        if editableState:
            ##Allow edition of the column
            itemFlags = Qt.ItemFlags(Qt.ItemIsEditable | itemFlags)

            if editableState == Eds.Multi:
                itemFlags = Qt.ItemFlags(ItemUserFlag.MultiEditable | itemFlags)

        self.setFlags(itemFlags)

    def hasChildren(self):
        if self.column() > 0:
            return False
        return self.__metaobj.hasChildren() if self.__metaobj else False

    @setWaitCursor
    def loadChildren(self):

        model = self.model()

        for child in self.__metaobj.iterChildren():
            rowItems = tuple(model.iterRowItems(child))
            self.appendRow(rowItems)

            for item in rowItems:
                if item.isValid():
                    item.loadData(item._metaprpty)

    def __repr__(self):
        sRepr = ("{0}('{1}')".format(self.__class__.__name__, self.text()))
        return sRepr

class PropertyItemModel(QtGui.QStandardItemModel):

    def __init__(self, metamodel, parent=None):
        super(PropertyItemModel, self).__init__(parent)

        self._metamodel = metamodel
        self.__iconProvider = None

        self.loadProperties(metamodel)
        self.setupHeaderData(metamodel)
        self.populateModel(metamodel)

        #self.rowsInserted.connect(self.onRowsInserted)
        #self.rowsMoved.connect(self.onRowsMoved)
        #self.columnsInserted.connect(self.onRowsInserted)

    def onRowsInserted(self, parentIndex, start, end):

        parentItem = self.itemFromIndex(parentIndex)
        if not parentItem:
            parentItem = self.invisibleRootItem()

        print parentItem, start, end

    def onRowsMoved(self, *args):
        print args

    def loadProperties(self, metamodel):

        sPropertyList = []
        propertiesDct = {}
        uiCategoryDct = {}

        sPrimePrptyList = []

        uiClassList = metamodel.listUiClasses()

        for uiClass in uiClassList:

            if not hasattr(uiClass, "primaryProperty"):
                sClsPrimePrpty = uiClass.propertiesDctItems[0][0]
                uiClass.primaryProperty = sClsPrimePrpty
            else:
                sClsPrimePrpty = uiClass.primaryProperty

            sPrimePrptyList.append(sClsPrimePrpty)

            for sProperty, propertyDct in uiClass.propertiesDctItems:

                if sProperty in sPropertyList:
                    continue

                if not propertyDct.get("uiVisible", False):
                    continue

                sPropertyList.append(sProperty)
                propertiesDct[sProperty] = propertyDct

                sCat = propertyDct.get("uiCategory", None)
                if not sCat:
                    sCat = "ZZ_Dev"
                    propertyDct["uiCategory"] = sCat

                if sCat != "ZZ_Dev":
                    uiCategoryDct.setdefault("XX_All", []).append(sProperty)

                uiCategoryDct.setdefault(sCat, []).append(sProperty)

        assert len(set(sPrimePrptyList)) == 1, "Multiple properties defined as primary: \n\t{0}".format("\n\t".join(sPrimePrptyList))
        sPrimePrpty = sPrimePrptyList[0]

        self.uiCategoryList = sorted(uiCategoryDct.iterkeys())

        self.propertyNames = []
        for sCat in self.uiCategoryList:
            if sCat != "XX_All":
                self.propertyNames.extend(uiCategoryDct[sCat])

        if self.propertyNames.index(sPrimePrpty) != 0:
            self.propertyNames.remove(sPrimePrpty)
            self.propertyNames.insert(0, sPrimePrpty)

        self.propertiesDct = propertiesDct
        self.uiCategoryDct = uiCategoryDct

    def getPrptiesFromUiCategory(self, categoryKey):

        if isinstance(categoryKey, basestring):
            sCategoryKey = categoryKey
        elif isinstance(categoryKey, int):
            sCategoryKey = toUnicode(self.uiCategoryList[categoryKey])

        return self.uiCategoryDct.get(sCategoryKey, ())

    def setupHeaderData(self, metamodel):

        self.setColumnCount(len(self.propertyNames))

        for c, sProperty in enumerate(self.propertyNames):

            propertyDct = self.propertiesDct[sProperty]

            sValue = propertyDct.get("uiDisplay", labelify(sProperty))
            self.setHeaderData(c, Qt.Horizontal, sValue, Qt.DisplayRole)

            sValue = propertyDct.get("uiToolTip", labelify(sProperty))
            self.setHeaderData(c, Qt.Horizontal, sValue, Qt.ToolTipRole)

    def populateModel(self, metamodel):

        for childobj in metamodel._rootobj.iterChildren():
            rowItems = tuple(self.iterRowItems(childobj))
            self.appendRow(rowItems)

            for item in rowItems:
                if item.isValid():
                    item.loadData(item._metaprpty)

    def iterRowItems(self, metaobj):

        for sProperty in self.propertyNames:
            metaProperty = metaobj.metaProperty(sProperty)
            yield PropertyItem(metaProperty)

    def hasChildren(self, parentIndex):

        if not parentIndex.isValid():
            return True

        if parentIndex.column() > 0:
            return False

        return self.itemFromIndex(parentIndex).hasChildren()

    def canFetchMore(self, parentIndex):

        if not parentIndex.isValid():
            return False

        if parentIndex.column() > 0:
            return False

        parentItem = self.itemFromIndex(parentIndex)
        return parentItem.hasChildren() and not parentItem.childrenLoaded

    def fetchMore(self, parentIndex):

        if not parentIndex.isValid():
            return

        parentItem = self.itemFromIndex(parentIndex)

        if parentItem.childrenLoaded:
            return

        parentItem.childrenLoaded = True
        parentItem.loadChildren()

    def setIconProvider(self, provider):
        self.__iconProvider = provider

    def iconProvider(self):

        if not self.__iconProvider:
            self.__iconProvider = QtGui.QFileIconProvider()

        return self.__iconProvider

    def __repr__(self):

        try:
            sRepr = ('{0}( "{1}" )'.format(self.__class__.__name__, self.objectName()))
        except:
            sRepr = self.__class__.__module__ + "." + self.__class__.__name__

        return sRepr
