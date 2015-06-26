

import os
ospth = os.path
import re
import fnmatch
import json
import stat

from distutils import file_util

from .sysutils import toUnicode, argToList


def isDirStat(statobj):
    return stat.S_ISDIR(statobj.st_mode)

def isFileStat(statobj):
    return stat.S_ISREG(statobj.st_mode)

def normPath(path):
    return ospth.normpath(path).replace("\\", "/")

def joinPath(*args):
    try:
        p = ospth.join(*args)
    except UnicodeDecodeError:
        p = ospth.join(*tuple(toUnicode(arg) for arg in args))

    return normPath(p)

def resolvePath(path):
    return normPath(ospth.expanduser(ospth.expandvars(path)))

def ignorePatterns(*patterns):
    """Function that can be used as iterPaths() ignore parameters.

    Patterns is a sequence of glob-style patterns
    that are used to exclude files"""
    def _ignore_patterns(path, names):
        ignored_names = []
        for pattern in patterns:
            ignored_names.extend(fnmatch.filter(names, pattern))
        return set(ignored_names)
    return _ignore_patterns

def iterPaths(sRootDirPath, **kwargs):

    if not ospth.isdir(sRootDirPath):
        raise ValueError, 'No such directory found: "{0}"'.format(sRootDirPath)

    bFiles = kwargs.pop("files", True)
    bDirs = kwargs.pop("dirs", True)
    bRecursive = kwargs.pop("recursive", True)

    ignoreDirsFunc = kwargs.get("ignoreDirs", None)
    ignoreFilesFunc = kwargs.get("ignoreFiles", None)

    for sDirPath, sDirNames, sFileNames in os.walk(sRootDirPath):

        if not bRecursive:
            del sDirNames[:] #don't walk further

        if ignoreDirsFunc is not None:
            sIgnoredDirs = ignoreDirsFunc(sDirPath, sDirNames)
            for sDir in sIgnoredDirs:
                try: sDirNames.remove(sDir)
                except ValueError: pass

        if bDirs:
            for sDir in sDirNames:
                yield addTrailingSlash(joinPath(sDirPath, sDir))

        if ignoreFilesFunc is not None:
            sIgnoredFiles = ignoreFilesFunc(sDirPath, sFileNames)

        if bFiles:
            for sFileName in sFileNames:

                if sFileName in sIgnoredFiles:
                    continue

                yield joinPath(sDirPath, sFileName)

def addTrailingSlash(sDirPath):
    return sDirPath if sDirPath.endswith("/") else sDirPath + "/"

def commonDir(sPathList):
    sDir = ospth.commonprefix(sPathList)
    return sDir if (sDir[-1] in ("\\", "/")) else (ospth.dirname(sDir) + "/")

def copyFile(sSrcFilePath, sDestPath, **kwargs):

    if ospth.normcase(sSrcFilePath) == ospth.normcase(sDestPath):
        raise ValueError, "Path of source and destination files are the same."

    return file_util.copy_file(sSrcFilePath, sDestPath, **kwargs)

def copyTree(in_sSrcRootDir, in_sDestRootDir, **kwargs):

    bDryRun = kwargs.get("dry_run", False)

    bPrintSrcOnly = kwargs.pop("printSourceOnly", False)
    sFilePathList = kwargs.pop("filePaths", "NoEntry")

    sReplaceExtDct = kwargs.pop("replaceExtensions", kwargs.pop("replaceExts", {}))
    if not isinstance(sReplaceExtDct, dict):
        raise TypeError, '"replaceExtensions" kwarg expects {0} but gets {1}.'.format(dict, type(sReplaceExtDct))

    sEncryptExtList = kwargs.pop("encryptExtensions", kwargs.pop("encryptExts", []))
    if not isinstance(sEncryptExtList, list):
        raise TypeError, '"encryptExtensions" kwarg expects {0} but gets {1}.'.format(list, type(sEncryptExtList))

    if sEncryptExtList:
        raise NotImplementedError, "Sorry, feature has been removed."
        #import cryptUtil
        sEncryptExtList = list(e.strip(".") for e in sEncryptExtList)

    sSrcRootDir = addTrailingSlash(normPath(in_sSrcRootDir))
    sDestRootDir = addTrailingSlash(normPath(in_sDestRootDir))

    if not ospth.isdir(sSrcRootDir):
        raise ValueError, 'No such directory found: "{0}"'.format(sSrcRootDir)

    if not ospth.isdir(sDestRootDir):
        print 'Creating destination directory: "{0}"'.format(sDestRootDir)
        if not bDryRun:
            os.makedirs(sDestRootDir)

    sCopiedFileList = []

    if sFilePathList == "NoEntry":

        raise NotImplementedError, "Sorry, but for now, you must provide a list of file paths to copy."

    else:

        sFilePathList = argToList(sFilePathList)
        sFilePathList.sort()

        srcRootDirRexp = re.compile("^" + sSrcRootDir, re.I)
        destRootDirRexp = re.compile("^" + sDestRootDir, re.I)

        # building destination directories
        sDestDirList = sFilePathList[:]

        iMaxPathLen = 0
        for i, sFilePath in enumerate(sFilePathList):

            sSrcDir = addTrailingSlash(normPath(ospth.dirname(sFilePath)))

            sRexpList = srcRootDirRexp.findall(sSrcDir)
            if not sRexpList:
                raise RuntimeError, "File outside of source directory: {0}.".format(sSrcDir)

            sDestDirList[i] = sSrcDir.replace(sRexpList[0], sDestRootDir)

            iPathLen = len(srcRootDirRexp.split(sFilePath, 1)[1])
            if iPathLen > iMaxPathLen:
                iMaxPathLen = iPathLen

        iNumFiles = len(sFilePathList)
        iDoneFileCount = 0
        iCountLen = len(str(iNumFiles)) * 2 + 5

        sPrintFormat = "{0:^{width1}} {1:<{width2}} >> {2}"
        sPrintFormat = sPrintFormat if not bPrintSrcOnly else sPrintFormat.split(">>", 1)[0]

        def endCopy(sFilePath, sDestPath, bCopied, iDoneFileCount):

            iDoneFileCount += 1

            if bCopied:
                sCount = "{0}/{1}".format(iDoneFileCount, iNumFiles)
                print sPrintFormat.format(sCount
                                        , srcRootDirRexp.split(sFilePath, 1)[1]
                                        , destRootDirRexp.split(sDestPath, 1)[1]
                                        , width1=iCountLen
                                        , width2=iMaxPathLen)

                sCopiedFileList.append(sDestPath)

            return iDoneFileCount

        print '{0} files to copy from "{1}" to "{2}":'.format(iNumFiles, sSrcRootDir, sDestRootDir)

        #creating directories
        for sDestDir in sorted(set(sDestDirList)):
            if (not ospth.isdir(sDestDir)) and (not bDryRun):
                os.makedirs(sDestDir)

        #copying files
        if sReplaceExtDct:

            for sFilePath, sDestDir in zip(sFilePathList, sDestDirList):

                sPath, sExt = ospth.splitext(sFilePath); sExt = sExt.strip(".")
                sNewExt = sReplaceExtDct.get(sExt, "")
                if sNewExt:
                    sDestPath = joinPath(sDestDir, ospth.basename(sPath)) + "." + sNewExt.strip(".")
                else:
                    sDestPath = joinPath(sDestDir, ospth.basename(sFilePath))

                bCopied = True
                if sExt in sEncryptExtList:
                    pass#bCopied = cryptUtil.encryptFile(sFilePath, sDestPath, **kwargs)
                else:
                    sDestPath, bCopied = copyFile(sFilePath, sDestPath, **kwargs)

                iDoneFileCount = endCopy(sFilePath, sDestPath, bCopied, iDoneFileCount)

        elif sEncryptExtList:

            for sFilePath, sDestDir in zip(sFilePathList, sDestDirList):

                sExt = ospth.splitext(sFilePath)[1].strip(".")

                #print "\t{0} >> {1}".format( srcRootDirRexp.split( sFilePath, 1 )[1], destRootDirRexp.split( sDestDir, 1 )[1] )

                sDestPath = joinPath(sDestDir, ospth.basename(sFilePath))

                bCopied = True
                if sExt in sEncryptExtList:
                    pass#bCopied = cryptUtil.encryptFile(sFilePath, sDestPath, **kwargs)
                else:
                    _, bCopied = copyFile(sFilePath, sDestPath, **kwargs)

                iDoneFileCount = endCopy(sFilePath, sDestPath, bCopied, iDoneFileCount)

        else:

            for sFilePath, sDestDir in zip(sFilePathList, sDestDirList):

                sDestPath = joinPath(sDestDir, ospth.basename(sFilePath))

                _, bCopied = copyFile(sFilePath, sDestPath, **kwargs)

                iDoneFileCount = endCopy(sFilePath, sDestPath, bCopied, iDoneFileCount)

    return sCopiedFileList

def jsonWrite(sFile, obj, **kwargs):
    with open(sFile, mode='wb') as fp:
        json.dump(obj, fp, indent=2, encoding='utf-8', **kwargs)

def jsonRead(sFile):
    with open(sFile, 'rb') as fp:
        obj = json.load(fp, encoding='utf-8')
    return obj
