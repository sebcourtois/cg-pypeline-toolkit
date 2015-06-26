

from pytk.util.sysutils import MemSize

from pytk.core.metaproperty import BasePropertyFactory
from pytk.core.metaproperty import MetaProperty
from pytk.core.metaproperty import EditState as Eds
from pytk.core.metaobject import MetaObject

DrcEntryProperties = (
('name',
    {
    'type': 'drc_info',
    'isMulti':False,
    'storable':"fileName",
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiCategory':'01_General',
    'uiDecorated':True,
    }
),
('modifTime',
    {
    'type': 'drc_time',
    'isMulti':False,
    'storable':'lastModified',
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':'Modif. Date',
    'uiCategory':'01_General',
    }
),
('creationTime',
    {
    'type': 'drc_time',
    'isMulti':False,
    'storable':'created' ,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':'Creation Date',
    'uiCategory':'01_General',
    }
),
)

DrcFileProperties = [
('suffix',
    {
    'type': 'drc_info',
    'isMulti':False,
    'default':'',
    'storable':False,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':'Type',
    'uiCategory':'01_General',
    }
),
('fileSize',
    {
    'type': 'drc_size',
    'isMulti':False,
    'storable':'size',
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':'Size',
    'uiCategory':'01_General',
    }
),
]
DrcFileProperties.extend(DrcEntryProperties)

class FileInfoProperty(MetaProperty):

    def read(self):
        value = getattr(self._metaobj._qfileinfo, self.storageName)
        return value() if callable(value) else value

    def write(self, value):
        return True

class FileTimeProperty(FileInfoProperty):

    def read(self):
        return FileInfoProperty.read(self).toPython()

class FileSizeProperty(FileInfoProperty):

    def read(self):
        return MemSize(FileInfoProperty.read(self))

    def displayText(self):
        return "{0:.0cM}".format(self.getattr_())

class PropertyFactory(BasePropertyFactory):

    propertyTypeDct = {
    'drc_info' : FileInfoProperty,
    'drc_time' : FileTimeProperty,
    'drc_size' : FileSizeProperty,
    }


class DrcMetaObject(MetaObject):

    propertyFactoryClass = PropertyFactory






