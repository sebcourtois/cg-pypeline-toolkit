
import os
import re
from datetime import datetime
import filecmp

from PySide.QtCore import QDir

from pytk.core.dialogs import confirmDialog

from pytk.util.logutils import logMsg
from pytk.util.qtutils import toQFileInfo
from pytk.util.fsutils import pathJoin# , pathResolve
from pytk.util.fsutils import copyFile, getLatestFile
from pytk.util.fsutils import sha1HashFile
from pytk.util.qtutils import setWaitCursor
# from pytk.util.sysutils import toUtf8
from pytk.util.external.send2trash import send2trash

from .properties import DrcMetaObject
from .properties import DrcEntryProperties, DrcFileProperties
from .utils import promptForComment
from .utils import findVersionFields, addVersionSuffixes, formattedVersion
from .utils import LockFile

class DrcEntry(DrcMetaObject):

    classUiPriority = 0

    propertiesDctItems = DrcEntryProperties
    propertiesDct = dict(propertiesDctItems)

    primaryProperty = propertiesDctItems[0][0] # defines which property will be displayed as a Tree in UI.

    def __init__(self, drcLibrary, drcPath=None):

        self.library = drcLibrary
        self._qfileinfo = None
        self._qdir = None

        self.loadedChildren = []
        self.childrenLoaded = False

        super(DrcEntry, self).__init__()

        fileInfo = toQFileInfo(drcPath)
        if fileInfo:
            self.loadData(fileInfo)

    def loadData(self, fileInfo):

        fileInfo.setCaching(True)

        qfileinfo = self._qfileinfo
        if qfileinfo and qfileinfo == qfileinfo:
            fileInfo.refresh()
            self._qdir.refresh()
        else:
            self._qfileinfo = fileInfo
            sAbsPath = fileInfo.absoluteFilePath()

            self._qdir = QDir(sAbsPath)
            self._qdir.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.AllDirs)

        super(DrcEntry, self).loadData()

        sEntryName = self.name
        self.baseName, self.suffix = os.path.splitext(sEntryName)
        self.label = sEntryName

        self._remember()

        fileInfo.setCaching(False)

    def addModelRow(self, parent):

        model = self.library._itemmodel
        if not model:
            return

        parentPrpty = parent.metaProperty(model.primaryProperty)

        for parentItem in parentPrpty.viewItems:
            model.loadRowItems(self, parentItem)

    def delModelRow(self):

        model = self.library._itemmodel
        primePrpty = self.metaProperty(model.primaryProperty)

        for primeItem in primePrpty.viewItems:

            parentItem = primeItem.parent()
            parentItem.removeRow(primeItem.row())

        primePrpty.viewItems = []

    def updateModelRow(self):
        logMsg(log='all')

        model = self.library._itemmodel
        if not model:
            return

        primePrpty = self.metaProperty(model.primaryProperty)
        for primeItem in primePrpty.viewItems:
            primeItem.updateRow()

    def parent(self):
        return self.library.getEntry(self._qfileinfo.absolutePath())

    def loadChildren(self):

        self.childrenLoaded = True

        for child in self.iterChildren():
            child.addModelRow(self)
            self.loadedChildren.append(child)

    def refresh(self, children=False, parent=None):
        logMsg(log="all")

        if self._writingValues_:
            return

        logMsg('Refreshing : {0}'.format(self), log='debug')

        fileInfo = self._qfileinfo

        if not fileInfo.exists():
            self._forget(parent, recursive=True)
        else:
            self.loadData(fileInfo)
            self.updateModelRow()

            if children and self.childrenLoaded:

                oldChildren = self.loadedChildren[:]
                for child in self.iterChildren():
                    if child not in oldChildren:
                        child.addModelRow(self)
                        self.loadedChildren.append(child)

                for child in oldChildren:
                    child.refresh(children=children, parent=self)

    def isPublic(self):
        return self.library.space == "public"

    def isPrivate(self):
        return self.library.space == "private"

    def iterChildren(self):
        getEntry = self.library.getEntry
        return (getEntry(info) for info in self._qdir.entryInfoList())

    def hasChildren(self):
        return False

    def pathname(self):
        return self._qfileinfo.absoluteFilePath()

    def getIconData(self):
        return self._qfileinfo

    def sendToTrash(self):
        send2trash(self.pathname())
        self.refresh(children=True)

    def _remember(self):

        key = self.pathname()
        loadedEntriesCache = self.library.loadedEntriesCache

        if key in loadedEntriesCache:
            logMsg("Already loaded : {0}.".format(self), log="debug")
        else:
            loadedEntriesCache[key] = self

    def _forget(self, parent=None, **kwargs):
        logMsg(self.__class__.__name__, log='all')

        bRecursive = kwargs.get("recursive", True)

        if bRecursive:

            for child in self.loadedChildren[:]:
                child._forget(parent, **kwargs)

        return self.__forgetOne(parent)


    def __forgetOne(self, parent=None):

        key = self.pathname()
        loadedEntriesCache = self.library.loadedEntriesCache

        if key not in loadedEntriesCache:
            logMsg("Already dropped : {0}.".format(self), log="debug")
        else:
            parentDir = parent if parent else self.parent()
            if parentDir:
                parentDir.loadedChildren.remove(self)

            del self.loadedChildren[:]

            self.delModelRow()

            return loadedEntriesCache.pop(key)


    def __getattr__(self, sAttrName):

        member = self._qfileinfo
        if hasattr(member, sAttrName):
            return getattr(member, sAttrName)
        else:
            s = "'{}' object has no attribute '{}'".format(type(self).__name__, sAttrName)
            raise AttributeError(s)

    def __cmp__(self, other):

        if not isinstance(other, self.__class__):
            return cmp(1 , None)

        return cmp(self.pathname() , other.pathname())

class DrcDir(DrcEntry):

    classUiPriority = 1

    def __init__(self, drcLibrary, drcPath=None):
        super(DrcDir, self).__init__(drcLibrary, drcPath)

    def getHomonym(self, sSpace):

        curLib = self.library
        homoLib = curLib.getHomonym(sSpace)

        sHomoLibPath = homoLib.pathname()
        sHomoPath = re.sub("^" + curLib.pathname(), sHomoLibPath, self.pathname())

        return homoLib.getEntry(sHomoPath)

    def suppress(self):
        parentDir = self.parent()
        if parentDir._qdir.rmdir(self.name):
            self.refresh(children=True, parent=parentDir)

    def hasChildren(self):
        return True

class DrcFile(DrcEntry):

    classUiPriority = 2

    propertiesDctItems = DrcFileProperties

    propertiesDct = dict(propertiesDctItems)

    def __init__(self, drcLibrary, drcPath=None):
        super(DrcFile, self).__init__(drcLibrary, drcPath)


    def loadData(self, fileInfo):

        sUser = self.library.project.getLoggedUser().loginName
        self._lockfile = LockFile(fileInfo.absoluteFilePath(), sUser)

        DrcEntry.loadData(self, fileInfo)

    def edit(self):
        logMsg(log='all')

        bLockState = self.getPrpty("locked")
        if not self.setLocked(True):
            return

        try:
            self.makePrivateCopy()
        except:
            self.setLocked(bLockState)
            raise

    def makePrivateCopy(self, **kwargs):

        sPubFilePath = self.pathname()

        assert self.isFile(), "File does NOT exist !"
        assert self.isPublic(), "File in PRIVATE library !"

        sPubDirPath, sPubFilenameWithExt = os.path.split(sPubFilePath)

        # converting the file directory path from public to private
        pubLib = self.library
        privLib = pubLib.getHomonym("private")

        sPubLibPath = pubLib.pathname()
        sPrivLibPath = privLib.pathname()

        sPrivDirPath = re.sub("^" + sPubLibPath, sPrivLibPath, sPubDirPath)

        # adding version suffixes to filename

        v = formattedVersion('v', self.getLatestVersion() + 1)
        w = formattedVersion('w', 0)
        sPrivFilenameWithExt = addVersionSuffixes(sPubFilenameWithExt, v, w)

        # at this point, file path is fully converted
        sPrivFilePath = pathJoin(sPrivDirPath, sPrivFilenameWithExt)

        if sPubFilePath == sPrivFilePath:
            raise ValueError('Path of source and destination files are identical: "{0}".'
                             .format(sPubFilePath))

        bForce = kwargs.pop("force", False)
        bDryRun = kwargs.get("dry_run", False)

        if not os.path.exists(sPrivDirPath):
            if not bDryRun:
                os.makedirs(sPrivDirPath)

        bSameFiles = False

        if (not bForce) and os.path.exists(sPrivFilePath):

            bSameFiles = filecmp.cmp(sPubFilePath, sPrivFilePath, shallow=True)

            if not bSameFiles:

                privFileTime = datetime.fromtimestamp(os.path.getmtime(sPrivFilePath))
                pubFileTime = datetime.fromtimestamp(os.path.getmtime(sPubFilePath))

                sState = "an OLDER" if privFileTime < pubFileTime else "a NEWER"

                sMsg = """
You have {0} version of '{1}':

    private file: {2}
    public  file: {3}
""".format(sState, sPrivFilenameWithExt,
           privFileTime.strftime("%A, %d-%m-%Y %H:%M"),
           pubFileTime.strftime("%A, %d-%m-%Y %H:%M"),
           )
                sConfirm = confirmDialog(title='WARNING !'
                                        , message=sMsg.strip('\n')
                                        , button=[ 'Keep', 'Overwrite', 'Cancel']
                                        , icon="warning")

                if sConfirm == 'Cancel':
                    logMsg("Cancelled !", warning=True)
                    return ""
                elif sConfirm == 'Keep':
                    return sPrivFilePath

        if bSameFiles:
            logMsg('\nAlready copied "{0}" \n\t to: "{1}"'.format(sPubFilePath, sPrivFilePath))
        else:
            copyFile(sPubFilePath, sPrivFilePath, **kwargs)
            logMsg('\nCopied "{0}" \n\t to: "{1}"'.format(sPubFilePath, sPrivFilePath))

        return sPrivFilePath


    def _incrementDamNode(self, sComment):
        return self.setPrpty("comment", sComment)# self.node.increment(toUtf8(sComment))

    def differsFrom(self, sOtherFilePath):

        sOtherSha1Key = ""

        sCurFilePath = self.pathname()

        if os.path.normcase(sOtherFilePath) == os.path.normcase(sCurFilePath):
            return False, sOtherSha1Key

        sOwnSha1Key = self.getPrpty("hashKey")
        if not sOwnSha1Key:
            return True, sOtherSha1Key

        sOtherSha1Key = sha1HashFile(sOtherFilePath)
        bDiffers = (sOtherSha1Key != sOwnSha1Key)

        return bDiffers, sOtherSha1Key

    @setWaitCursor
    def incrementVersion(self, sSrcFilePath, **kwargs):

        bAutoUnlock = kwargs.pop("autoUnlock", False)
        bSaveSha1Key = kwargs.pop("saveSha1Key", False)

        bDiffers, sSrcSha1Key = self.differsFrom(sSrcFilePath)
        if not bDiffers:
            logMsg("Skipping {0} increment: Files are identical.".format(self))
            return True

        backupFile = None

        try:
            sComment, backupFile, bLockState = self.beginPublish(**kwargs)
        except RuntimeError, e:
            return self.abortPublish(e, backupFile, bAutoUnlock)

        try:
            copyFile(sSrcFilePath, self.pathname())
        except Exception, e:
            return self.abortPublish(e, backupFile, bAutoUnlock)

        if not self._incrementDamNode(sComment):
            return self.abortPublish("Version increment failed", backupFile, bAutoUnlock)

        self.endPublish(sSrcFilePath, autoUnlock=bAutoUnlock, saveSha1Key=bSaveSha1Key,
                        sha1Key=sSrcSha1Key, lockState=bLockState)

        return True

    def getPrivateDir(self):

        assert self.isFile(), "File does NOT exist !"
        assert self.isPublic(), "File in PRIVATE library !"

        pubDir = self.parent()
        privDir = pubDir.getHomonym("private")
        return privDir

    def getLatestVersion(self):
        sFileName = getLatestFile(self.getBackupDir().pathname(), self.name)
        if not sFileName:
            v = 0
        else:
            vers = findVersionFields(sFileName)
            v = int(vers[0].strip('v')) if vers else 0

        return v

    def getLatestBackupFile(self):

        sBkupDirPath = self.getBackupDir().pathname()
        sFileName = getLatestFile(sBkupDirPath, self.name)

        if not sFileName:
            return None

        sFilePath = pathJoin(sBkupDirPath, sFileName)
        return self.library.getEntry(sFilePath)


    def versionFromName(self):
        vers = findVersionFields(self.name)
        return int(vers[0].strip('v')) if vers else 0

    def getBackupDir(self):

        sDirPath = pathJoin(self.parent().pathname(), "_version")
        if not os.path.exists(sDirPath):
            os.mkdir(sDirPath)

        return self.library.getEntry(sDirPath)


    def createBackup(self, **kwargs):

#         if not self.checkPathOnDisk(space="server", confirm=False):
#             return None

        v = formattedVersion('v', self.getLatestVersion() + 1)
        sBkupFilename = addVersionSuffixes(self.name, v)

        backupDir = self.getBackupDir()
        sBkupFilePath = pathJoin(backupDir.pathname(), sBkupFilename)
        if os.path.exists(sBkupFilePath):
            raise RuntimeError, "Backup file already exists: \n\t> '{}'".format(sBkupFilePath)

        _, bCopied = copyFile(self.pathname(), sBkupFilePath)
        if not bCopied:
            raise RuntimeError, "Backup file could not be copied: \n\t> '{}'".format(sBkupFilePath)

        backupFile = self.library.getEntry(sBkupFilePath)

        return backupFile

    def abortPublish(self, sErrorMsg, backupFile=None, autoUnlock=False):

        if backupFile:

            sBkupFilePath = backupFile.pathname()
            sCurFilePath = self.pathname()
            bSameFiles = filecmp.cmp(sCurFilePath, sBkupFilePath, shallow=True)
            if not bSameFiles:
                copyFile(sBkupFilePath, sCurFilePath)

            backupFile.remove()

        if autoUnlock:
            self.setLocked(False)

        sMsg = "Publishing aborted: {0}".format(sErrorMsg)
        logMsg(sMsg , warning=True)

        return False

    def beginPublish(self, **kwargs):

        sComment = kwargs.pop("comment", "")

        self.refresh()

        bLockState = self.getPrpty("locked")
        if not kwargs.pop("autoLock", False):

            if not bLockState:

                msg = '"{0}" is not locked !'.format(self.name)

                confirmDialog(title='SORRY !'
                            , message=msg
                            , button=["OK"]
                            , defaultButton="OK"
                            , cancelButton="OK"
                            , dismissString="OK")

                raise RuntimeError, msg

        if not self.setLocked(True):
            raise RuntimeError, "Could not lock the file !"


        if not sComment:
            sComment = promptForComment(text=self.getPrpty("comment"))

            if not sComment:
                self.setLocked(bLockState)
                raise RuntimeError, "Please, provide a comment !"


        backupFile = self.createBackup(**kwargs)
        if not backupFile:
            self.setLocked(bLockState)
            raise RuntimeError, "Could not create backup file !"

        return sComment, backupFile, bLockState

    def endPublish(self, sSrcFilePath, autoUnlock=False, saveSha1Key=False,
                    sha1Key="", lockState="NoEntry"
                    ):

        if saveSha1Key:

            if not sha1Key:
                sNewSha1Key = sha1HashFile(sSrcFilePath)
            else:
                sNewSha1Key = sha1Key

            self.setPrpty("hashKey", sNewSha1Key)

        self.setPrpty("sourceFile", sSrcFilePath)

        if autoUnlock:
            self.setLocked(False)
        elif lockState != "NoEntry":
            self.setLocked(lockState)

        self.refresh()

        return True

    def setLocked(self, bLock, **kwargs):
        logMsg(log='all')

        sLockOwner = self.getLockOwner()
        sLoggedUser = self.library.project.getLoggedUser(force=True).loginName

        if sLockOwner:
            if sLockOwner == sLoggedUser:
                if bLock:
                    return True
            else:
                if kwargs.get("warn", True):
                    self.warnLockedBySomeone(sLockOwner)
                    return False

        if self.setPrpty('locked', bLock):
            self.refresh()# must be done to get "lock" property updated
            return True

        return False

    def getLockOwner(self):

        if self.getPrpty("locked"):
            sLockOwner = self.getPrpty("lockOwner")
            if not sLockOwner:
                raise ValueError, 'Invalid value for lockOwner: "{0}"'.format(self)
            return sLockOwner

        return ""

    def warnLockedBySomeone(self, sLockOwner, **kwargs):
        sMsg = '{1}\n\n{2:^{0}}\n\n{3:^{0}}'.format(len(self.name) + 2, '"{0}"'.format(self.name), "locked by", (sLockOwner + " !").upper())
        confirmDialog(title="FILE LOCKED !"
                    , message=sMsg
                    , button=["OK"]
                    , defaultButton="OK"
                    , cancelButton="OK"
                    , dismissString="OK"
                    , icon=kwargs.pop("icon", "critical"))
        return

    def suppress(self):
        parentDir = self.parent()
        if parentDir._qdir.remove(self.name):
            self.refresh(children=True, parent=parentDir)

