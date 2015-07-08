

from pytk.core.authenticator import Authenticator

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

        if not proj.init():
            return None

        return proj

    def reset(self):
        logMsg(log='all')

        self._damas = None
        self._authobj = None
        self.authenticated = False

        self._itemmodel = None
        self.loadedLibraries = {}

    def getAuthenticator(self):

        sAuthFullName = self.getVar("project", "authenticator", "")
        if not sAuthFullName:
            return Authenticator()
        else:
            sAuthMod, sAuthClass = sAuthFullName.rsplit(".", 1)
            exec("from {} import {}".format(sAuthMod, sAuthClass))

            return eval(sAuthClass)()

    def isAuthenticated(self):

        bAuth = self._authobj.authenticated

        if not bAuth:
            logMsg("The project is not authenticated.", warning=True)

        return bAuth

    def init(self, **kwargs):
        logMsg(log='all')

        self.reset()

        try:
            self.__confobj = PyConfParser(getConfigModule(self.name))
        except ImportError, msg:
            if kwargs.pop("warn", True):
                logMsg(msg , warning=True)
            return None

        self._authobj = self.getAuthenticator()
        userData = self._authobj.authenticate()
        print userData

        if not self.isAuthenticated():
            return False

        return True

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
        return self.__confobj.getVar(sSection, sVarName, default=default, **kwargs)

    def getPath(self, sSpace, sLibName, sRcVar="NoEntry"):

        sRcPath = self.getVar(sLibName, sSpace + "_path")
        if sRcVar != "NoEntry":
            return pathJoin(sRcPath, self.getVar(sLibName, sRcVar))

        return sRcPath

    def listUiClasses(self):
        return DrcLibrary.listUiClasses()

    def setItemModel(self, model):
        self._itemmodel = model
        for lib in self.loadedLibraries.itervalues():
            lib.setItemModel(model)

    def iterChildren(self):
        return self.loadedLibraries.itervalues()

    def editFile(self, drcFile):
        pass


class DamUser(object):

    def __init__(self, project):
        pass

