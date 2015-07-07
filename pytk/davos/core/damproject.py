

from pytk.core.dialogs import loginDialog

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

        self._damas = None
        self._shotgun = None
        self.authenticated = False

        self._propertyItemModel = None
        self.loadedLibraries = {}

    def init(self, **kwargs):
        logMsg(log='all')

        self.reset()

        if self._shotgun:
            self.authenticate()

        if not self.isAuthenticated():
            return False

        self.loadLibraries()

        return True

    def getLoggedUser(self, *args, **kwargs):
        self._shotgun.getLoggedUser(*args, **kwargs)
        return {}

    def login(self, *args, **kwargs):
        self._shotgun.loginUser(*args, **kwargs)
        return {}

    def logout(self, *args, **kwargs):
        self._shotgun.logoutUser(*args, **kwargs)
        self.reset()
        logMsg("Signed out !" , warning=True)

    def authenticate(self, **kwargs):

        if kwargs.get('relog', False):
            self.logout()

        userData = self.getLoggedUser()
        if userData:
            # logMsg( "Already authenticated", log = 'info' )
            self.authenticated = True

        if not self.authenticated:
            userData = loginDialog(loginFunc=self.login)

        if self.authenticated:
            pass
            # should initiate user class

        return True

    def isAuthenticated(self):
        if self.authenticated:
            return True
        else:
            logMsg("The project is not authenticated.", warning=True)
            return False

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




class DamUser(object):

    def __init__(self, project):
        pass

