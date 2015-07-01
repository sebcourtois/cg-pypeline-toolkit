
from pytk.util.sysutils import listClassesFromModule
from pytk.util.qtutils import toQFileInfo

from . import drctypes
from .drctypes import DrcEntry
from .drctypes import DrcDir

class DrcLibrary(object):

    def __init__(self, sLibName, sRootPath):

        self.loadedEntriesCache = {}

        self.name = sLibName
        self._rootobj = DrcDir(self, sRootPath)

    def listUiClasses(self):
        return sorted((cls for (_, cls) in listClassesFromModule(drctypes.__name__)
                                if hasattr(cls, "classUiPriority")), key=lambda c: c.classUiPriority)

    def entry(self, drcPath):

        fileInfo = toQFileInfo(drcPath)

        drcEntry = self.loadedEntriesCache.get(fileInfo.absoluteFilePath())
        if drcEntry:
            drcEntry.loadData(fileInfo)
            return drcEntry

        return DrcEntry(self, fileInfo)

    def getPath(self):
        return self._rootobj.pathname
