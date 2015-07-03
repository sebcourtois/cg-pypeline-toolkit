
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

    def __new__(cls, drcLibrary, drcPath=None, space=""):

        fileInfo = toQFileInfo(drcPath)

        if (cls is DrcEntry):
            if fileInfo.isDir():
                cls = DrcDir
            elif fileInfo.isFile():
                cls = DrcFile

        return super(DrcEntry, cls).__new__(cls)

    def __init__(self, drcLibrary, drcPath=None):

        self.library = drcLibrary
        self._qfileinfo = None
        self._qdir = None

        super(DrcEntry, self).__init__()

        fileInfo = toQFileInfo(drcPath)
        if fileInfo:
            self.loadData(fileInfo)

    def loadData(self, fileInfo):

        fileInfo.setCaching(True)

        if not self._qfileinfo:
            self._qfileinfo = fileInfo
        else:
            self._qfileinfo.refresh()

        self.pathname = fileInfo.absoluteFilePath()

        if not self._qdir:
            self._qdir = QDir(self.pathname)
            self._qdir.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.AllDirs)
        else:
            self._qdir.refresh()

        DrcMetaObject.loadData(self)

        sEntryName = self.name
        self.baseName, self.suffix = os.path.splitext(sEntryName)
        self.label = sEntryName

        self.__remember()

        fileInfo.setCaching(False)

    def refresh(self):
        self.loadData(self._qfileinfo)

    def isPublic(self):
        return self.library.space == "public"

    def isPrivate(self):
        return self.library.space == "private"

    def iterChildren(self):
        entry = self.library.entry
        return (entry(child) for child in self._qdir.entryInfoList())

    def hasChildren(self):
        return False

    def getIconData(self):
        return self._qfileinfo

    def __remember(self):

        key = self.pathname
        loadedEntriesCache = self.library.loadedEntriesCache

        if key in loadedEntriesCache:
            logMsg("Already remembered : {0}.".format(self), log="debug")
        else:
            loadedEntriesCache[key] = self

    def __forget(self):

        key = self.pathname
        loadedEntriesCache = self.library.loadedEntriesCache

        if key not in loadedEntriesCache:
            logMsg("Already forgotten : {0}.".format(self), log="debug")
        else:
            return loadedEntriesCache.pop(key)

    def __getattr__(self, sAttrName):

        member = self._qfileinfo
        if hasattr(member, sAttrName):
            return getattr(member, sAttrName)
        else:
            s = "'{}' object has no attribute '{}'".format(type(self).__name__, sAttrName)
            raise AttributeError(s)


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

        sPubFilePath = self.pathname

        assert self.isFile(), "No such file: '{0}'".format(sPubFilePath)
        assert self.isPublic(), "File is not public: '{0}'".format(sPubFilePath)

        sPubDirPath, sPubFilenameWithExt = os.path.split(sPubFilePath)

        # converting the file directory path from public to private
        pubLib = self.library
        privLib = pubLib.getHomonym("private")

        sPubLibPath = pubLib.getPath()
        sPrivLibPath = privLib.getPath()

        sPrivDirPath = re.sub("^" + sPubLibPath, sPrivLibPath, sPubDirPath)

        # adding version suffixes to filename
        sPubFilename, sExt = os.path.splitext(sPubFilenameWithExt)

        sVersion = 'v{:03d}'.format(0)
        sWipNum = 'w{:03d}'.format(0)

        sPrivFilenameWithExt = ".".join((sPubFilename, sVersion, sWipNum)) + sExt

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
            print bEqualFiles

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

