
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

        storableValue = propertyDct.get("storable", True)
        self.storageName = storableValue if storableValue and isinstance(storableValue, basestring) else sProperty
        self.__storable = bool(storableValue)

        self._metaobj = metaobj

        self.name = sProperty
        self.propertyDct = propertyDct

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

    def isStorable(self):
        return self.__storable

    def isValidValue(self, value):
        return True

    def getattr_(self, *args):
        return getattr(self._metaobj, self.name, *args)

    def getPresetValues(self):
        return None, True

    def __repr__(self):

        try:
            sRepr = ('{0}( "{1}" )'.format("Property", self.name))
        except:
            sRepr = self.__class__.__name__

        return sRepr


class BasePropertyFactory(object):

    propertyTypeDct = {}

    def __new__(cls, sProperty, metaobj):

        sPropertyType = metaobj.__class__.propertiesDct[sProperty]["type"]
        PropertyClass = cls.propertyTypeDct[sPropertyType]
        return PropertyClass(sProperty, metaobj)
