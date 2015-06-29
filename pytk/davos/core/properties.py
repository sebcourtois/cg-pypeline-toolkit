

from pytk.util.sysutils import MemSize

from pytk.core.metaproperty import BasePropertyFactory
from pytk.core.metaproperty import MetaProperty
from pytk.core.metaproperty import EditState as Eds
from pytk.core.metaobject import MetaObject

DrcEntryProperties = (
('name',
    {
    'type':'drc_info',
    'isMulti':False,
    'accessor':'_qfileinfo',
    'read':'fileName()',
    'storable':False,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiCategory':'01_General',
    'uiDecorated':True,
    }
),
('modifTime',
    {
    'type':'drc_time',
    'isMulti':False,
    'accessor':'_qfileinfo',
    'read':'lastModified()',
    'storable':False,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':'Modif. Date',
    'uiCategory':'01_General',
    }
),
('creationTime',
    {
    'type':'drc_time',
    'isMulti':False,
    'accessor':'_qfileinfo',
    'read':'created()',
    'storable':False,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':'Creation Date',
    'uiCategory':'01_General',
    }
),
)

DrcFileProperties = [

('fileSize',
    {
    'type':'drc_size',
    'isMulti':False,
    'accessor':'_qfileinfo',
    'read':'size()',
    'storable':False,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':'Size',
    'uiCategory':'01_General',
    }
),
]
DrcFileProperties.extend(DrcEntryProperties)

class FileInfoProperty(MetaProperty):

    def __init__(self, *args):
        super(FileInfoProperty, self).__init__(*args)

class FileTimeProperty(FileInfoProperty):

    def read(self):
        return FileInfoProperty.read(self).toPython()

class FileSizeProperty(FileInfoProperty):

    def read(self):
        return MemSize(FileInfoProperty.read(self))


class PropertyFactory(BasePropertyFactory):

    propertyTypeDct = {
    'drc_info' : FileInfoProperty,
    'drc_time' : FileTimeProperty,
    'drc_size' : FileSizeProperty,
    }


class DrcMetaObject(MetaObject):

    propertyFactoryClass = PropertyFactory






