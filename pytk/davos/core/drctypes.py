
import os
import re
from datetime import datetime
import filecmp

from PySide.QtCore import QDir

from pytk.core.dialogs import confirmDialog

from pytk.util.logutils import logMsg
from pytk.util.qtutils import toQFileInfo
from pytk.util.fsutils import pathJoin# , pathResolve
from pytk.util.fsutils import copyFile

from .properties import DrcMetaObject
from .properties import DrcEntryProperties, DrcFileProperties


class DrcEntry(DrcMetaObject):

    classUiPriority = 0

    propertiesDctItems = DrcEntryProperties
    propertiesDct = dict(propertiesDctItems)

    primaryProperty = propertiesDctItems[0][0] # defines which property will be displayed as a Tree in UI.

    def __init__(self, drcLibrary, drcPath=None):

        self.library = drcLibrary
        self._qfileinfo = None
        self._qdir = None

        self.loadedChildren = []
        self.childrenLoaded = False

        super(DrcEntry, self).__init__()

        fileInfo = toQFileInfo(drcPath)
        if fileInfo:
            self.loadData(fileInfo)

    def loadData(self, fileInfo):

        fileInfo.setCaching(True)

        qfileinfo = self._qfileinfo
        if qfileinfo and qfileinfo == qfileinfo:
            fileInfo.refresh()
            self._qdir.refresh()
        else:
            self._qfileinfo = fileInfo
            sAbsPath = fileInfo.absoluteFilePath()

            self._qdir = QDir(sAbsPath)
            self._qdir.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.AllDirs)

        super(DrcEntry, self).loadData()

        sEntryName = self.name
        self.baseName, self.suffix = os.path.splitext(sEntryName)
        self.label = sEntryName

        self._remember()

        fileInfo.setCaching(False)

    def addModelRow(self, parent):

        model = self.library._itemmodel
        if not model:
            return

        parentPrpty = parent.metaProperty(model.primaryProperty)

        for parentItem in parentPrpty.viewItems:
            model.loadRowItems(self, parentItem)

    def delModelRow(self):

        model = self.library._itemmodel
        primePrpty = self.metaProperty(model.primaryProperty)

        for primeItem in primePrpty.viewItems:

            parentItem = primeItem.parent()
            parentItem.removeRow(primeItem.row())

        primePrpty.viewItems = []

    def updateModelRow(self):
        logMsg(log='all')

        model = self.library._itemmodel
        if not model:
            return

        primePrpty = self.metaProperty(model.primaryProperty)

        for primeItem in primePrpty.viewItems:
            primeItem.updateRow()

    def parent(self):
        return self.library.getEntry(self._qfileinfo.absolutePath())

    def loadChildren(self):

        self.childrenLoaded = True

        for child in self.iterChildren():
            child.addModelRow(self)
            self.loadedChildren.append(child)

    def refresh(self, parent=None):
        logMsg(log="all")

        if self._writingValues_:
            return

        logMsg('Refreshing : {0}'.format(self), log='debug')

        fileInfo = self._qfileinfo

        if not fileInfo.exists():
            self._forget(recursive=True)
            if parent:
                parent.loadedChildren.remove(self)
        else:
            self.loadData(fileInfo)
            self.updateModelRow()

            if self.childrenLoaded:

                oldChildren = self.loadedChildren[:]
                for child in self.iterChildren():
                    if child not in oldChildren:
                        child.addModelRow(self)
                        self.loadedChildren.append(child)

                for child in oldChildren:
                    child.refresh(parent=self)

    def isPublic(self):
        return self.library.space == "public"

    def isPrivate(self):
        return self.library.space == "private"

    def iterChildren(self):
        getEntry = self.library.getEntry
        return (getEntry(info) for info in self._qdir.entryInfoList())

    def hasChildren(self):
        return False

    def pathname(self):
        return self._qfileinfo.absoluteFilePath()

    def getIconData(self):
        return self._qfileinfo

    def _remember(self):

        key = self.pathname()
        loadedEntriesCache = self.library.loadedEntriesCache

        if key in loadedEntriesCache:
            logMsg("Already loaded : {0}.".format(self), log="debug")
        else:
            loadedEntriesCache[key] = self

    def __forgetOne(self):

        key = self.pathname()
        loadedEntriesCache = self.library.loadedEntriesCache

        if key not in loadedEntriesCache:
            logMsg("Already dumped : {0}.".format(self), log="debug")
        else:
            self.delModelRow()
            return loadedEntriesCache.pop(key)

    def _forget(self, **kwargs):
        logMsg(self.__class__.__name__, log='all')

        bRecursive = kwargs.get("recursive", True)

        if bRecursive:

            for child in self.loadedChildren[:]:
                child._forget(**kwargs)

        self.__forgetOne()

    def __getattr__(self, sAttrName):

        member = self._qfileinfo
        if hasattr(member, sAttrName):
            return getattr(member, sAttrName)
        else:
            s = "'{}' object has no attribute '{}'".format(type(self).__name__, sAttrName)
            raise AttributeError(s)

    def __cmp__(self, other):

        if not isinstance(other, self.__class__):
            return cmp(1 , None)

        return cmp(self.pathname() , other.pathname())

class DrcDir(DrcEntry):

    classUiPriority = 1

    def __init__(self, drcLibrary, drcPath=None):
        super(DrcDir, self).__init__(drcLibrary, drcPath)

    def hasChildren(self):
        return True

class DrcFile(DrcEntry):

    classUiPriority = 2

    propertiesDctItems = DrcFileProperties

    propertiesDct = dict(propertiesDctItems)

    def __init__(self, drcLibrary, drcPath=None):
        super(DrcFile, self).__init__(drcLibrary, drcPath)

    def makePrivateCopy(self, **kwargs):

        sPubFilePath = self.pathname()

        assert self.isFile(), "No such file: '{0}'".format(sPubFilePath)
        assert self.isPublic(), "File is not public: '{0}'".format(sPubFilePath)

        sPubDirPath, sPubFilenameWithExt = os.path.split(sPubFilePath)

        # converting the file directory path from public to private
        pubLib = self.library
        privLib = pubLib.getHomonym("private")

        sPubLibPath = pubLib.pathname()
        sPrivLibPath = privLib.pathname()

        sPrivDirPath = re.sub("^" + sPubLibPath, sPrivLibPath, sPubDirPath)

        # adding version suffixes to filename
        sPubFilename, sExt = os.path.splitext(sPubFilenameWithExt)

        sVersion = 'v{:03d}'.format(0)
        sWipNum = 'w{:03d}'.format(0)

        sPrivFilenameWithExt = "-".join((sPubFilename, sVersion, sWipNum)) + sExt

        # at this point, file path is fully converted
        sPrivFilePath = pathJoin(sPrivDirPath, sPrivFilenameWithExt)

        if sPubFilePath == sPrivFilePath:
            raise ValueError('Path of source and destination files are identical: "{0}".'
                             .format(sPubFilePath))

        bForce = kwargs.pop("force", False)
        bDryRun = kwargs.get("dry_run", False)

        if not os.path.exists(sPrivDirPath):
            if not bDryRun:
                os.makedirs(sPrivDirPath)

        bEqualFiles = False

        if (not bForce) and os.path.exists(sPrivFilePath):

            bEqualFiles = filecmp.cmp(sPubFilePath, sPrivFilePath, shallow=True)

            if not bEqualFiles:

                privFileTime = datetime.fromtimestamp(os.path.getmtime(sPrivFilePath))
                pubFileTime = datetime.fromtimestamp(os.path.getmtime(sPubFilePath))

                sState = "an OLDER" if privFileTime < pubFileTime else "a NEWER"

                sMsg = """
You have {0} version of '{1}':

    private file: {2}
    public  file: {3}
""".format(sState, sPrivFilenameWithExt,
           privFileTime.strftime("%A, %d-%m-%Y %H:%M"),
           pubFileTime.strftime("%A, %d-%m-%Y %H:%M"),
           )
                sConfirm = confirmDialog(title='WARNING !'
                                        , message=sMsg.strip('\n')
                                        , button=[ 'Keep', 'Overwrite', 'Cancel']
                                        , icon="warning")

                if sConfirm == 'Cancel':
                    logMsg("Cancelled !", warning=True)
                    return ""
                elif sConfirm == 'Keep':
                    return sPrivFilePath

        if bEqualFiles:
            logMsg('\nAlready copied "{0}" \n\t to: "{1}"'.format(sPubFilePath, sPrivFilePath))
        else:
            copyFile(sPubFilePath, sPrivFilePath, **kwargs)
            logMsg('\nCopied "{0}" \n\t to: "{1}"'.format(sPubFilePath, sPrivFilePath))

        return sPrivFilePath


