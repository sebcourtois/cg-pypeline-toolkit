
from pytk.util.logutils import logMsg
from pytk.util.sysutils import argToTuple
from pytk.util.sysutils import toStr
from pytk.util.strutils import upperFirst

from .metaproperty import BasePropertyFactory

class MetaObject(object):

    classReprAttr = "name"

    propertiesDctItems = ()
    propertiesDct = {}

    presetByPropertyDct = {}

    propertyFactoryClass = BasePropertyFactory

    def __init__(self):

        self._writingValues_ = False
        self.__metaProperties = {}

        for sProperty, _ in self.__class__.propertiesDctItems:

            metaProperty = self.__class__.propertyFactoryClass(sProperty, self)
            setattr(self, metaProperty.name, metaProperty.defaultValue)

            self.__metaProperties[sProperty] = metaProperty

        logMsg(self.__class__.__name__, log='all')

    def loadData(self):
        logMsg(self.__class__.__name__, log='all')

        for sProperty, _ in self.__class__.propertiesDctItems:

            metaProperty = self.__metaProperties[sProperty]
            if metaProperty.isReadable():
                setattr(self, metaProperty.name, metaProperty.read())

    def metaProperty(self, sProperty):
        return self.__metaProperties.get(sProperty)

    def iterProperties(self, sPropertyList):

        for sProperty in sPropertyList:
            yield self.metaProperty(sProperty)

    def hasPrpty(self, sProperty):
        return sProperty in self.__metaProperties

    def getPrpty(self, sProperty, default="NoEntry"):
        logMsg(self.__class__.__name__, log='all')

        if default == "NoEntry":
            return getattr(self, sProperty)
        else:
            return getattr(self, sProperty, default)

    def setPrpty(self, sProperty, value, writeValue=True):
        logMsg(self.__class__.__name__, log='all')

        metaProperty = self.__metaProperties[sProperty]

        if metaProperty.isValidValue(value):

            if writeValue:
                if not metaProperty.write(value):
                    return False

            setattr(self, metaProperty.name, value)

            return True

        else:
            logMsg(" {0}.{1} : Invalid value : '{2}'".format(self, sProperty, value) , warning=True)
            return False

    def getPrptyCfg(self, sProperty, key, default="NoEntry"):

        cls = self.__class__

        assert sProperty in cls.propertiesDct

        if default == "NoEntry":
            return cls.propertiesDct[sProperty][key]
        else:
            return cls.propertiesDct[sProperty].get(key, default)

    def createPrptyEditor(self, sProperty, parentWidget):

        assert sProperty in self.__metaProperties
        metaProperty = self.__metaProperties[sProperty]

        return metaProperty.createEditorWidget(parentWidget)

    def getPrptyValueFromWidget(self, sProperty, wdg):

        assert sProperty in self.__metaProperties
        metaProperty = self.__metaProperties[sProperty]

        return metaProperty.getValueFromWidget(wdg)

    def castValueForPrpty(self, sProperty, value):

        assert sProperty in self.__metaProperties
        metaProperty = self.__metaProperties[sProperty]

        if isinstance(value, (tuple, list)):
            return list(metaProperty.castValue(v) for v in value)
        else:
            return metaProperty.castValue(value)

    def __writeAllValues(self, customPrptyDctItems=None):
        logMsg(self.__class__.__name__, log='all')

        cls = self.__class__

        if customPrptyDctItems is None:
            customPrptyDctItems = cls.propertiesDctItems

        for sProperty, _ in customPrptyDctItems:

            value = getattr(self, sProperty)

            bJustSetPrpty = False

            sSetFnc = "".join(("set", sProperty[0].upper(), sProperty[1:]))
            setFnc = getattr(self, sSetFnc, None)

            msg = "Setting {0}.{1} to {2}( {3} ) using {4}".format(
                    self, sProperty, type(value).__name__, toStr(value), setFnc if setFnc else "setPrpty")
            logMsg(msg, log="debug")

            bSuccess = False
            if setFnc:

                try:
                    bSuccess = setFnc(value, writingAttrs=True)
                except TypeError:
                    try:
                        bSuccess = setFnc(value)
                    except Exception, msg:
                        logMsg(msg , warning=True)
                        bJustSetPrpty = True
            else:
                bJustSetPrpty = True

            if bJustSetPrpty:
                metaProperty = self.__metaProperties[sProperty]
                bSuccess = metaProperty.write(value)

            if not bSuccess:
                logMsg("Failed " + msg, warning=True)

    def writeAllValues(self, customPrptyDctItems=None):

        self._writingValues_ = True
        try:
            return self.__writeAllValues(customPrptyDctItems)
        finally:
            self._writingValues_ = False

    def initPropertiesFromKwargs(self, **kwargs):
        logMsg(self.__class__.__name__, log='all')

        logMsg("Entered kwargs:", kwargs, log="debug")

        bIgnoreMissing = kwargs.pop("ignoreMissingKwarg", False)

        cls = self.__class__

        # get all keyword arguments
        for sProperty, _ in cls.propertiesDctItems:
            metaProperty = self.__metaProperties[sProperty]

            if metaProperty.defaultValue == "undefined" and not bIgnoreMissing:

                try:
                    value = kwargs.pop(metaProperty.name)
                except KeyError:
                    msg = '{0} needs "{1}" kwarg at least'.format(cls.__name__, metaProperty.name)
                    raise TypeError, msg

                else:
                    setattr(self, metaProperty.name, value)

            else:
                value = kwargs.pop(metaProperty.name, metaProperty.defaultValue)
                setattr(self, metaProperty.name, value)

        logMsg("Remaining kwargs:", kwargs, log="debug")

        return kwargs

    def createInputDataUI(self, parentWidget, **kwargs):
        cls = self.__class__
        logMsg(cls.__name__, log='all')

        sIgnorePrpty = kwargs.pop("ignoreInputData", [])
        sIgnorePrptyList = argToTuple(sIgnorePrpty)

        inputWdgItems = []

        for sProperty, _ in cls.propertiesDctItems:
            if sProperty in sIgnorePrptyList:
                continue

            metaProperty = self.__metaProperties[sProperty]
            if metaProperty.isInput():

                inputWdg = metaProperty.createEditorWidget(parentWidget)
                inputWdgItems.append((metaProperty.name , { "widget" : inputWdg }))

        return inputWdgItems

    def getPrptyPreset(self, sProperty):

        """ Do nothing by default. Should be reimplemented in sub-classes"""

        assert sProperty in self.__class__.propertiesDct

        return None, True


    def __repr__(self):

        cls = self.__class__

        try:
            sClsName = upperFirst(cls.classLabel) if hasattr(cls, "classLabel") else cls.__name__
            sRepr = ("{0}('{1}')".format(sClsName, getattr(self, cls.classReprAttr)))
        except AttributeError:
            sRepr = cls.__name__

        return sRepr
