
from PySide.QtCore import QFileInfo

from pytk.util.logutils import logMsg

from pytk.util.sysutils import listClassesFromModule, getCaller
from pytk.util.qtutils import toQFileInfo

from . import drctypes
from .drctypes import DrcEntry, DrcDir, DrcFile
from pytk.util.fsutils import pathNorm

class DrcLibrary(DrcEntry):

    classLabel = "library"
    classReprAttr = "fullName"
    classUiPriority = 0

    def __init__(self, sLibName, sLibPath, sSpace="", project=None):

        self.loadedEntriesCache = {}
        self._itemmodel = None

        self.libName = sLibName
        self.fullName = DrcLibrary.makeFullName(sSpace, sLibName)
        self.space = sSpace
        self.project = project

        super(DrcLibrary, self).__init__(self, sLibPath)

    def loadData(self, fileInfo):
        logMsg(log="all")

        if self.project:
            self._itemmodel = self.project._itemmodel

        super(DrcLibrary, self).loadData(fileInfo)
        assert self.isDir(), "<{}> No such directory: '{}'".format(self, self.pathname())

        self.label = self.fullName

    def setItemModel(self, model):
        self._itemmodel = model

    def addModelRow(self):

        model = self._itemmodel
        if model:
            model.loadRowItems(self, model)

    @staticmethod
    def makeFullName(*names):
        return "|".join(names)

    @staticmethod
    def listUiClasses():
        return sorted((cls for (_, cls) in listClassesFromModule(drctypes.__name__)
                                if hasattr(cls, "classUiPriority")), key=lambda c: c.classUiPriority)

    def getEntry(self, pathOrInfo):
        logMsg(log="all")

        fileInfo = None
        if isinstance(pathOrInfo, QFileInfo):
            sEntryPath = pathOrInfo.absoluteFilePath()
            fileInfo = pathOrInfo
        elif isinstance(pathOrInfo, basestring):
            sEntryPath = pathNorm(pathOrInfo)
        else:
            raise TypeError(
                    "argument 'pathOrInfo' must be of type <QFileInfo> or <basestring>. Got {0}."
                    .format(type(pathOrInfo)))

        drcEntry = self.loadedEntriesCache.get(sEntryPath)
        if drcEntry:
            drcEntry.loadData(drcEntry._qfileinfo)
            return drcEntry

        if not fileInfo:
            fileInfo = toQFileInfo(sEntryPath)

        entryCls = DrcEntry
        if fileInfo.isDir():
            entryCls = DrcDir
        elif fileInfo.isFile():
            entryCls = DrcFile

        return entryCls(self, fileInfo)

    def getHomonym(self, sSpace):

        if self.space == sSpace:
            return None

        return self.project.getLibrary(sSpace, self.libName)

    def hasChildren(self):
        return True

    def _remember(self):

        key = self.fullName
        cacheDict = self.project.loadedLibraries

        if key in cacheDict:
            logMsg("<{}> Already loaded : {}.".format(getCaller(depth=4, fo=False), self), log="debug")
        else:
            cacheDict[key] = self

    def _forget(self):

        key = self.fullName
        cacheDict = self.project.loadedLibraries

        if key not in cacheDict:
            logMsg("<{}> Already dumped : {}.".format(getCaller(depth=4, fo=False), self), log="debug")
        else:
            return cacheDict.pop(key)

