

from datetime import datetime

from pytk.util.sysutils import MemSize

from pytk.core.metaproperty import BasePropertyFactory
from pytk.core.metaproperty import MetaProperty
from pytk.core.metaproperty import EditState as Eds
from pytk.core.metaobject import MetaObject

DrcEntryProperties = (
('name',
    {
    'type': 'drc_path',
    'isMulti':False,
    'storable':False,
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
    'storable':'st_mtime',
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
    'storable':'st_ctime' ,
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
    'type': 'drc_path',
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
    'storable':'st_size',
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':'Size',
    'uiCategory':'01_General',
    }
),
]
DrcFileProperties.extend(DrcEntryProperties)

class PathProperty(MetaProperty):

    def read(self):
        return getattr(self._metaobj._pathobj, self.storageName)

    def write(self, value):
        return True

class StatProperty(MetaProperty):

    def read(self):

        statobj = self._metaobj._cached_stat
        if statobj is None:
            statobj = self._metaobj._pathobj.stat()

        return getattr(statobj, self.storageName)

    def write(self, value):
        return True

class StatTimeProperty(StatProperty):

    def read(self):
        return datetime.fromtimestamp(StatProperty.read(self))

class StatSizeProperty(StatProperty):

    def read(self):
        return MemSize(StatProperty.read(self))

    def displayText(self):
        return "{0:.0cM}".format(self.getattr_())

class PropertyFactory(BasePropertyFactory):

    propertyTypeDct = {
    'drc_path' : PathProperty,
    'drc_stat' : StatProperty,
    'drc_time' : StatTimeProperty,
    'drc_size' : StatSizeProperty,
    }


class DrcMetaObject(MetaObject):

    propertyFactoryClass = PropertyFactory






