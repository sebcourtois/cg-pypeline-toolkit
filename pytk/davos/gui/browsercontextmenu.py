
from PySide import QtGui

from pytk.core.itemviews.basecontextmenu import BaseContextMenu
from pytk.core.dialogs import confirmDialog

from pytk.util.sysutils import toStr
from pytk.util.logutils import logMsg

# from pytk.util.fsutils import pathNorm
# from pytk.util.logutils import forceLog
from pytk.davos.core.drctypes import DrcFile


class BrowserContextMenu(BaseContextMenu):

    def __init__(self, parentView):
        super(BrowserContextMenu, self).__init__(parentView)

    def getActionSelection(self):

        view = self.view
        model = view.model()

        selectedItems = BaseContextMenu.getActionSelection(self)
        if not selectedItems:
            viewRootItem = model.itemFromIndex(view.rootIndex())
            if viewRootItem:
                selectedItems.append(viewRootItem)

        return selectedItems

    def getActionsConfig(self):

        # proj = self.model().metamodel

        actionsCfg = (
        { "label":"Edit"                , "fnc":self.editFile                   , "menu": "Main"},

        { "label":"separator"                                                   , "menu": "Main"},
        { "label":"Publish Version"     , "fnc":self.publishVersion             , "menu": "Main"},

        { "label":"separator"                                                                                , "menu": "Main"},
        { "label":"Off"                 , "fnc":self.setFilesLocked        , "args":[False]    , "menu": "Set Lock" },
        { "label":"On"                  , "fnc":self.setFilesLocked        , "args":[True]        , "menu": "Set Lock" },

        { "label":"Remove"              , "dev":True, "fnc":self.removeItems    , "menu": "Advanced" },

        { "label":"separator"           , "dev":False                           , "menu": "Main"},
        { "label":"Refresh"             , "fnc":self.refreshItems               , "menu": "Main" },
        )

        return actionsCfg

    # @forceLog(log='all')
    def editFile(self, *itemList):

        drcFile = itemList[-1]._metaobj

        try:
            drcFile.edit()
        except Exception, e:
            confirmDialog(title='SORRY !'
                        , message=toStr(e)
                        , button=["OK"]
                        , defaultButton="OK"
                        , cancelButton="OK"
                        , dismissString="OK"
                        , icon="critical")

    editFile.auth_types = ("DrcFile",)


    def setFilesLocked(self, bLock, *itemList):

        drcFiles = (item._metaobj for item in itemList)

        sAction = "Lock" if bLock else "Unlock"

        for df in drcFiles:
            df.refresh()
            if df.setLocked(bLock):
                logMsg('{0} {1}.'.format(sAction + "ed", df))

        return True

    setFilesLocked.auth_types = [ "DrcFile" ]


    # @forceLog(log='all')
    def refreshItems(self, *itemList, **kwargs):

        for item in itemList:
            item._metaobj.refresh(children=True)

    def removeItems(self, *itemList):

        entryList = tuple(item._metaobj for item in itemList)

        sEntryList = "\n    " .join(entry.name for entry in entryList)

        sMsg = 'Are you sure you want to delete these resources: \n\n    ' + sEntryList

        sConfirm = confirmDialog(title='WARNING !',
                                message=sMsg,
                                button=['OK', 'Cancel'],
                                 defaultButton='Cancel',
                                 cancelButton='Cancel',
                                 dismissString='Cancel',
                                 icon="warning")

        if sConfirm == 'Cancel':
            return

        for entry in entryList:

            if entry.isPublic():
                logMsg(u"Cannot remove a public file: {}".format(entry.name) , warning=True)
                continue

            entry.sendToTrash()

    def publishVersion(self, *itemList):

        item = itemList[-1]
        drcFile = item._metaobj

        sErr = ""
        if type(drcFile) is not DrcFile:
            sErr = 'A {0} cannot be published.'.format(type(drcFile).__name__)

        if not sErr:
            try:
                privDir = drcFile.getPrivateDir()
            except AssertionError, e:
                sErr = toStr(e)
            else:
                if not privDir:
                    sErr = 'Could not found its private directory !'.format(type(drcFile).__name__)

        if sErr:
            sMsg = "Cannot publish a new version : \n\n    > "
            confirmDialog(title='SORRY !'
                        , message=sMsg + sErr
                        , button=["OK"]
                        , defaultButton="OK"
                        , cancelButton="OK"
                        , dismissString="OK"
                        , icon="critical")
            return

        sFilter = "File (*{0})".format(drcFile.suffix) if drcFile.suffix else ""
        sSrcFilePath, _ = QtGui.QFileDialog.getOpenFileName(None,
                                                            "You know what to do...",
                                                            privDir.pathname(),
                                                            sFilter
                                                            )
        if not sSrcFilePath:
            logMsg("Cancelled !", warning=True)
            return

        drcFile.incrementVersion(sSrcFilePath, autoLock=True)

    publishVersion.auth_types = ("DrcFile" ,)
