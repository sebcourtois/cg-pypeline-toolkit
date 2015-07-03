

from pytk.util.logutils import logMsg

from pytk.util.sysutils import listClassesFromModule
from pytk.util.qtutils import toQFileInfo

from . import drctypes
from .drctypes import DrcEntry, DrcDir
from .properties import DrcMetaObject
from .properties import DrcLibraryProperties

class DrcLibrary(DrcMetaObject):

    classReprAttr = "fullName"
    classUiPriority = 0

    propertiesDctItems = DrcLibraryProperties
    propertiesDct = dict(propertiesDctItems)

    primaryProperty = propertiesDctItems[0][0]

    def __init__(self, sLibName, sLibPath, sSpace="", project=None):
        super(DrcLibrary, self).__init__()

        self.loadedEntriesCache = {}

        self.name = sLibName
        self._rootDir = DrcDir(self, sLibPath)
        self.space = sSpace
        self.project = project
        self.fullName = DrcLibrary.makeFullName(sSpace, sLibName)

        self.loadData(project)

    def loadData(self, project):
        DrcMetaObject.loadData(self)

        self.label = self.fullName

        if project:
            self.__remember()

    def refresh(self):
        self.loadData(self.project)

    @staticmethod
    def makeFullName(*names):
        return "|".join(names)

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

    def getHomonym(self, sSpace):

        if self.space == sSpace:
            return None

        return self.project.getLibrary(sSpace, self.name)

    def getPath(self):
        return self._rootDir.pathname

    def hasChildren(self):
        return True

    def iterChildren(self):
        return self._rootDir.iterChildren()

    def getIconData(self):
        return self._rootDir.getIconData()

    def __remember(self):

        key = self.fullName
        cacheDict = self.project.loadedLibraries

        if key in cacheDict:
            logMsg("Already remembered : {0}.".format(self), log="debug")
        else:
            cacheDict[key] = self

    def __forget(self):

        key = self.fullName
        cacheDict = self.project.loadedLibraries

        if key not in cacheDict:
            logMsg("Already forgotten : {0}.".format(self), log="debug")
        else:
            return cacheDict.pop(key)

