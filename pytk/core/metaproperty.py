from functools import partial
from pytk.util.sysutils import copyOf

class EditState:
    Disabled = 0
    Enabled = 1
    Multi = 2


class MetaProperty(object):

    def __init__(self , sProperty, metaobj):

        propertyDct = metaobj.__class__.propertiesDct[sProperty]

        self.type = propertyDct["type"]
        self.__isMulti = propertyDct.get("isMulti", False)

        self.defaultValue = [] if self.__isMulti else copyOf(propertyDct.get("default", "undefined"))

        self._accessor = None

        sReader = propertyDct.get("read", sProperty)
        self.__readable = True if sReader else False
        self.__reader = sReader

        sWriter = propertyDct.get("write", "")
        self.__writable = True if sWriter else False
        self.__writer = sWriter

        self.__storable = propertyDct.get("storable", True)
        self.__copyable = propertyDct.get("copyable", False)

        self._metaobj = metaobj

        self.accessored = False

        self.name = sProperty
        self.propertyDct = propertyDct

    def initAccessors(self):

        if self.accessored:
            return

        self.accessored = True

        self._accessor = getattr(self._metaobj, self.propertyDct["accessor"])

        if self.isReadable():
            sReader = self.__reader
            if sReader.endswith("()"):
                self.__reader = getattr(self._accessor, sReader.rstrip("()"))
            else:
                self.__reader = partial(getattr, self._accessor, sReader.rstrip("()"))


        if self.isWritable():
            sWriter = self.__writer
            if sWriter.endswith("()"):
                self.__writer = getattr(self._accessor, sWriter.rstrip("()"))
            else:
                self.__writer = partial(getattr, self._accessor, sWriter.rstrip("()"))

    def getParam(self, sParam, default="NoEntry"):

        if default == "NoEntry":
            value = self.propertyDct[sParam]
        else:
            value = self.propertyDct.get(sParam, default)

        return copyOf(value)

    def isMulti(self):
        return self.__isMulti

    def isInput(self):
        return self.propertyDct.get("inputData", False)

    def isReadable(self):
        return self.__readable

    def isWritable(self):
        return self.__writable

    def isStorable(self):
        return self.__storable

    def isCopyable(self):
        return self.__copyable

    def isValidValue(self, value):
        return True

    def read(self):

        self.initAccessors()

        return self.__reader()

    def write(self, value):

        self.initAccessors()

        return self.__writer(value)

    def getattr_(self, *args):
        return getattr(self._metaobj, self.name, *args)

    def getPresetValues(self):
        return None, True

    def __repr__(self):

        cls = self.__class__

        try:
            sRepr = ("{0}('{1}')".format(cls.__name__, self.name))
        except AttributeError:
            sRepr = cls.__name__

        return sRepr


class BasePropertyFactory(object):

    propertyTypeDct = {}

    def __new__(cls, sProperty, metaobj):

        sPropertyType = metaobj.__class__.propertiesDct[sProperty]["type"]
        PropertyClass = cls.propertyTypeDct[sPropertyType]
        return PropertyClass(sProperty, metaobj)
