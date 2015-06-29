
import os

from PySide.QtCore import QDir

from pytk.util.logutils import logMsg
from pytk.util.sysutils import listClassesFromModule
#from pytk.util.fsutils import isDirStat, isFileStat
from pytk.util.qtutils import toQFileInfo

from .properties import DrcMetaObject
from .properties import DrcEntryProperties, DrcFileProperties

class DrcRepository(object):

    def __init__(self, sDrcLibName, drcLibRootDir):

        self.loadedEntriesCache = {}

        self.name = sDrcLibName
        self._rootobj = DrcDir(self, drcLibRootDir)

    def listUiClasses(self):

        return sorted((cls for (_, cls) in listClassesFromModule(__name__)
                                if hasattr(cls, "classUiPriority")), key=lambda c: c.classUiPriority)

    def entry(self, drcPath):

        drcPath = toQFileInfo(drcPath)

        drcEntry = self.loadedEntriesCache.get(drcPath.absoluteFilePath())
        if drcEntry:
            drcEntry.loadData(drcPath)
            return drcEntry

        return DrcEntry(self, drcPath)


class DrcEntry(DrcMetaObject):

    classUiPriority = 0

    propertiesDctItems = DrcEntryProperties
    propertiesDct = dict(propertiesDctItems)

    primaryProperty = propertiesDctItems[0][0] #defines which property will be displayed as a Tree in UI.

    def __new__(cls, drcLibrary, drcPath=None):

        drcPath = toQFileInfo(drcPath)

        if (cls is DrcEntry):
            if drcPath.isDir():
                cls = DrcDir
            elif drcPath.isFile():
                cls = DrcFile

        return super(DrcEntry, cls).__new__(cls)

    def __init__(self, drcLibrary, drcPath=None):

        self.library = drcLibrary
        super(DrcEntry, self).__init__()

        drcPath = toQFileInfo(drcPath)
        if drcPath:
            self.loadData(drcPath)

    def loadData(self, drcPath):

        fileInfo = toQFileInfo(drcPath)
        self._qfileinfo = fileInfo
        self.__pathname = fileInfo.absoluteFilePath()

        self._qdir = QDir(self.__pathname)
        self._qdir.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.AllDirs)

        fileInfo.setCaching(True)
        DrcMetaObject.loadData(self)
        fileInfo.setCaching(False)

        self.baseName, self.suffix = os.path.splitext(self.name)

        self.__remember()

    @property
    def pathname(self):
        return self.__pathname

    def exists(self):
        return self._qfileinfo.exists()


    def iterChildren(self):
        entry = self.library.entry
        return (entry(child) for child in self._qdir.entryInfoList())

    def hasChildren(self):
        return False

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
