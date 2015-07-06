
from pytk.util.pyconfparser import PyConfParser
from pytk.util.logutils import logMsg
from pytk.util.fsutils import pathJoin, pathResolve
from pytk.util.sysutils import importModule

from .drclibrary import DrcLibrary


BUDDY_SPACES = {
"public":"private",
"private":"public",
}


def getConfigModule(sProjectName):

    sConfigModule = sProjectName

    try:
        modobj = importModule(sConfigModule)
    except ImportError:
        sConfigModule = 'pytk.davos.config.' + sProjectName
        modobj = importModule(sConfigModule)

    reload(modobj)

    return modobj


class DamProject(object):

    def __new__(cls, sProjectName, **kwargs):
        logMsg(cls.__name__ , log='all')

        proj = object.__new__(cls)

        proj.reset()
        proj.name = sProjectName

        if kwargs.pop("empty", False):
            return proj

        try:
            proj.__confobj = PyConfParser(getConfigModule(sProjectName))
        except ImportError, msg:
            if kwargs.pop("warn", True):
                logMsg(msg , warning=True)
            return None

        # proj.cookieFilePath = pathJoin(proj.getPath(space="local"), "damas.lwp")

        return proj

    def reset(self):
        logMsg(log='all')

        self.damas = None
        self.authenticated = False

        self._propertyItemModel = None
        self.loadedLibraries = {}

    def loadLibraries(self):

        for sLibName in self.getVar("project", "libraries"):
            for sSpace in ("public", "private"):
                self.getLibrary(sSpace, sLibName)

    def getLibrary(self, sSpace, sLibName):

        sFullName = DrcLibrary.makeFullName(sSpace, sLibName)
        drcLib = self.loadedLibraries.get(sFullName, None)

        if not drcLib:
            sLibPath = pathResolve(self.getVar(sLibName, sSpace + "_path"))
            lib = DrcLibrary(sLibName, sLibPath, sSpace, self)
            lib.addModelRow()

        return drcLib

    def getVar(self, sSection, sVarName, default="NoEntry", **kwargs):
        return self.__confobj.getVar(sSection, sVarName, default="NoEntry", **kwargs)

    def getRcPath(self, sSpace, sLibName, sRcVar="NoEntry"):

        sRcPath = self.getVar(sLibName, sSpace + "_path")
        if sRcVar != "NoEntry":
            return pathJoin(sRcPath, self.getVar(sLibName, sRcVar))

        return sRcPath

    def listUiClasses(self):
        return DrcLibrary.listUiClasses()

    def setItemModel(self, model):
        self._propertyItemModel = model
        for lib in self.loadedLibraries.itervalues():
            lib.setItemModel(model)

    def iterChildren(self):
        return self.loadedLibraries.itervalues()

    def editFile(self, drcFile):
        pass






