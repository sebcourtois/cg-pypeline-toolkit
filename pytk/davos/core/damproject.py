
from pytk.util.pyconfparser import PyConfParser
from pytk.util.logutils import logMsg
from pytk.util.fsutils import pathJoin, pathResolve, pathNorm
from pytk.util.strutils import findFields

from .drclibrary import DrcLibrary
from .damtypes import DamUser
from .dummyauth import DummyAuth
from .utils import getConfigModule

LIBRARY_SPACES = ("public", "private")

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

        proj.loadLibraries()

        return proj

    def reset(self):
        logMsg(log='all')

        self._damas = None
        self._authobj = None
        self.authenticated = False

        self.__loggedUser = None

        self._itemmodel = None
        self.loadedLibraries = {}

    def init(self, **kwargs):
        logMsg(log='all')

        self.reset()

        try:
            self.__confobj = PyConfParser(getConfigModule(self.name))
        except ImportError, msg:
            if kwargs.pop("warn", True):
                logMsg(msg , warning=True)
            return None

        self.__confLibraries = self.getVar("project", "libraries")

        return self.authenticate(**kwargs)

    def getAuthenticator(self):

        sAuthFullName = self.getVar("project", "authenticator", "")
        if not sAuthFullName:
            return DummyAuth()
        else:
            sAuthMod, sAuthClass = sAuthFullName.rsplit(".", 1)
            exec("from {} import {}".format(sAuthMod, sAuthClass))

            return eval(sAuthClass)()

    def authenticate(self):

        self._authobj = self.getAuthenticator()
        userData = self._authobj.authenticate()

        if not self.isAuthenticated():
            return False

        self.__loggedUser = DamUser(self, userData)

        return True

    def isAuthenticated(self):

        bAuth = self._authobj.authenticated

        if not bAuth:
            logMsg("The project is not authenticated.", warning=True)

        return bAuth

    def getLoggedUser(self, **kwargs):
        logMsg(log='all')

        bForce = kwargs.get("force", False)

        if bForce and not self.isAuthenticated():
            self.authenticate(relog=True)

        return self.__loggedUser

    def _iterConfigLibraries(self, fullName=False):

        for sLibName in self.__confLibraries:
            for sSpace in LIBRARY_SPACES:
                if fullName:
                    yield DrcLibrary.makeFullName(sSpace, sLibName)
                else:
                    yield (sSpace, sLibName)

    def loadLibraries(self):

        for sSpace, sLibName in self._iterConfigLibraries():
            self.getLibrary(sSpace, sLibName)

    def getLibrary(self, sSpace, sLibName):

        sFullLibName = DrcLibrary.makeFullName(sSpace, sLibName)
        drcLib = self.loadedLibraries.get(sFullLibName, None)

        if not drcLib:
            sLibPath = pathResolve(self.getVar(sLibName, sSpace + "_path"))
            drcLib = DrcLibrary(sLibName, sLibPath, sSpace, self)
            drcLib.addModelRow()

        return drcLib

    def getVar(self, sSection, sVarName, default="NoEntry", **kwargs):
        return self.__confobj.getVar(sSection, sVarName, default=default, **kwargs)

    def getPath(self, sSpace, sLibName, pathVar="", tokens=None):

        self._assertSpaceAndLibName(sSpace, sLibName)

        sRcPath = self.getVar(sLibName, sSpace + "_path")
        if pathVar:
            sRcPath = pathJoin(sRcPath, self.getVar(sLibName, pathVar))

        sRcPath = pathResolve(sRcPath)

        if tokens is not None:

            fields = findFields(sRcPath)
            rest = set(fields) - set(tokens.iterkeys())
            if rest:
                msg = ("Cannot resolve path: '{}'. \n\tMissing tokens: {}"
                        .format(sRcPath, list(rest)))
                raise AssertionError(msg)

            return sRcPath.format(**tokens)

        return sRcPath

    def libraryFromPath(self, sEntryPath):

        sPath = pathNorm(sEntryPath)

        for drcLib in self.loadedLibraries.itervalues():
            if drcLib.contains(sPath):
                return drcLib

    def entryFromPath(self, sEntryPath):

        drcLib = self.libraryFromPath(sEntryPath)
        assert drcLib is not None, "Path is NOT from a KNOWN library !"

        return drcLib.getEntry(sEntryPath)

    def publishEditedVersion(self, sSrcFilePath, **kwargs):

        privFile = self.entryFromPath(sSrcFilePath)
        pubFile = privFile.getPublicFile()
        pubFile.assertFilePublishable(privFile)
        pubFile.incrementVersion(privFile, **kwargs)

    def listUiClasses(self):
        return DrcLibrary.listUiClasses()

    def setItemModel(self, model):
        self._itemmodel = model
        for lib in self.loadedLibraries.itervalues():
            lib.setItemModel(model)

    def iterChildren(self):
        return self.loadedLibraries.itervalues()

    def _assertSpaceAndLibName(self, sSpace, sLibName):

        if sSpace not in LIBRARY_SPACES:
            raise ValueError("No such space: '{}'. Expected: {}"
                            .format(sSpace, LIBRARY_SPACES))

        if sLibName not in self.__confLibraries:
            msg = ("No such library: '{}'. \n\n\tKnown libraries: {}"
                   .format(sLibName, self.__confLibraries))
            raise ValueError(msg)
