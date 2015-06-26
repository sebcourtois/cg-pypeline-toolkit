from pytk.util.logutils import logMsg
from pytk.util.sysutils import listClassesFromModule
from pytk.util.fsutils import isDirStat, isFileStat

from .utils import toPath
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

        drcPath = toPath(drcPath)
        try:
            drcStat = drcPath.stat()
        except OSError:
            drcStat = None

        drcEntry = self.loadedEntriesCache.get(drcPath)
        if drcEntry:
            drcEntry.loadData(drcPath, drcStat)
            return drcEntry

        return DrcEntry(self, drcPath, drcStat)


class DrcEntry(DrcMetaObject):

    classUiPriority = 0

    propertiesDctItems = DrcEntryProperties
    propertiesDct = dict(propertiesDctItems)

    primaryProperty = propertiesDctItems[0][0] #defines which property will be displayed as a Tree in UI.

    def __new__(cls, drcLibrary, drcPath=None, drcStat=None):

        drcPath = toPath(drcPath)

        if (cls is DrcEntry) and (drcStat is not None):
            if isDirStat(drcStat):
                cls = DrcDir
            elif isFileStat(drcStat):
                cls = DrcFile

        return super(DrcEntry, cls).__new__(cls)

    def __init__(self, drcLibrary, drcPath=None, drcStat=None):

        self.library = drcLibrary
        self._cached_stat = None
        super(DrcEntry, self).__init__()

        drcPath = toPath(drcPath)
        if drcPath:
            self.loadData(drcPath, drcStat)

    def loadData(self, drcPath, drcStat=None):

        self._pathobj = toPath(drcPath)

        try:
            self._cached_stat = drcStat if drcStat else self._pathobj.stat()
            DrcMetaObject.loadData(self)
        finally:
            self._cached_stat = None

        self.__remember()

    def pathname(self):
        return str(self._pathobj)

    def exists(self):
        return self._pathobj.exists()

    def stat(self):
        return self._cached_stat if self._cached_stat else self._pathobj.stat()

    def iterChildren(self):
        entry = self.library.entry
        return (entry(child) for child in self._pathobj.iterdir())

    def hasChildren(self):
        return False

    def __remember(self):

        key = self._pathobj
        loadedEntriesCache = self.library.loadedEntriesCache

        if key in loadedEntriesCache:
            logMsg("Already remembered : {0}.".format(self), log="debug")
        else:
            loadedEntriesCache[key] = self

    def __forget(self):

        key = self.pathname()
        loadedEntriesCache = self.library.loadedEntriesCache

        if key not in loadedEntriesCache:
            logMsg("Already forgotten : {0}.".format(self), log="debug")
        else:
            return loadedEntriesCache.pop(key)

class DrcDir(DrcEntry):

    classUiPriority = 1

    def __init__(self, drcLibrary, drcPath=None, drcStat=None):
        super(DrcDir, self).__init__(drcLibrary, drcPath, drcStat)

    def hasChildren(self):
        return True

class DrcFile(DrcEntry):

    classUiPriority = 2

    propertiesDctItems = DrcFileProperties

    propertiesDct = dict(propertiesDctItems)

    def __init__(self, drcLibrary, drcPath=None, drcStat=None):
        super(DrcFile, self).__init__(drcLibrary, drcPath, drcStat)
