
import sys

from pytk.util.pyconfparser import PyConfParser
from pytk.util.logutils import logMsg
from pytk.util.fsutils import pathJoin, pathResolve
#from pytk.util.strutils import underJoin

from .drclibrary import DrcLibrary


def getConfigModule(sProjectName):

    sConfigModule = 'pytk.davos.config.' + sProjectName

    __import__(sConfigModule)

    modobj = sys.modules.get(sConfigModule)
    reload(modobj)

    return modobj

BUDDY_SPACES = {
"public":"private",
"private":"public",
}

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

        #proj.cookieFilePath = pathJoin(proj.getPath(space="local"), "damas.lwp")
        proj.loadLibraries()

        return proj

    def reset(self):
        logMsg(log='all')

        self.damas = None
        self.authenticated = False

        self.loadedLibraries = {}

    def loadLibraries(self):

        for sLibName in self.getVar("project", "libraries"):
            for sSpace in ("public", "private"):
                self.loadLibrary(sSpace, sLibName)

    def loadLibrary(self, sSpace, sLibName):

        sLibPath = pathResolve(self.getVar(sLibName, sSpace + "_path"))
        drcLib = DrcLibrary(sLibName, sLibPath, sSpace, self)

        return drcLib

    def getLibrary(self, sSpace, sLibName):

        sFullName = DrcLibrary.makeFullName(sSpace, sLibName)
        drcLib = self.loadedLibraries.get(sFullName)

        return drcLib

    def getVar(self, sSection, sVarName, default="NoEntry", **kwargs):
        return self.__confobj.getVar(sSection, sVarName, default="NoEntry", **kwargs)


    def getLibPath(self, sSpace, sLibName, sPathVar="NoEntry"):

        sLibPath = self.getVar(sLibName, sSpace + "_path")
        if sPathVar != "NoEntry":
            return pathJoin(sLibPath, self.getVar(sLibName, sPathVar))

        return sLibPath

    def listUiClasses(self):
        return self.loadedLibraries.values()[0].listUiClasses()

    def iterChildren(self):
        return self.loadedLibraries.itervalues()

    def editFile(self, drcFile):
        pass






