

from pytk.util.sysutils import MemSize

from pytk.core.metaproperty import BasePropertyFactory
from pytk.core.metaproperty import MetaProperty
from pytk.core.metaproperty import EditState as Eds
from pytk.core.metaobject import MetaObject


DrcLibraryProperties = (
('label',
    {
    'type':'drc_base',
    'isMulti':False,
    'accessor':'',
    'read':'',
    'storable':False,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiCategory':'01_General',
    'uiDecorated':True,
    }
),
)

DrcEntryProperties = (
('label',
    {
    'type':'drc_base',
    'isMulti':False,
    'accessor':'',
    'read':'',
    'storable':False,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':'Name',
    'uiCategory':'01_General',
    'uiDecorated':True,
    }
),
('name',
    {
    'type':'drc_base',
    'isMulti':False,
    'accessor':'_qfileinfo',
    'read':'fileName()',
    'storable':False,
    'uiEditable':Eds.Disabled,
    'uiVisible':False,
    'uiCategory':'01_General',
    'uiDecorated':False,
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
# ('creationTime',
#     {
#     'type':'drc_time',
#     'isMulti':False,
#     'accessor':'_qfileinfo',
#     'read':'created()',
#     'storable':False,
#     'uiEditable':Eds.Disabled,
#     'uiVisible':True,
#     'uiDisplay':'Creation Date',
#     'uiCategory':'01_General',
#     }
# ),
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
('lockOwner',
    {
    'type':'drc_base',
    'isMulti':False,
    'default':'',
    'accessor':'_lockfile',
    'read':'owner()',
    'storable':False,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':"Locked by",
    'uiCategory':"05_File",
    }
),
('locked',
    {
    'type':'drc_base',
    'isMulti':False,
    'default':False,
    'accessor':'_lockfile',
    'read':'is_locked()',
    'write':'set_locked()',
    'storable':False,
    'uiEditable':Eds.Disabled,
    'uiVisible':False,
    'uiDisplay':"",
    'uiCategory':"05_File",
    }
),
('currentVersion',
    {
    'type':'drc_base',
    'isMulti':False,
    'default':'',
    'accessor':'',
    'read':'',
    'storable':False,
    'copyable':True,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':"Version",
    'uiCategory':"05_File",
    }
),
('comment',
    {
    'type':'drc_base',
    'isMulti':False,
    'default':'',
    'accessor':'',
    'read':'',
    'storable':False,
    'copyable':True,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':'',
    'uiCategory':None,
    }
),
('hashKey',
    {
    'type':'drc_base',
    'isMulti':False,
    'default':'',
    'accessor':'',
    'read':'',
    'storable':False,
    'copyable':True,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':'',
    'uiCategory':None,
    }
),
('sourceFile',
    {
    'type':'drc_base',
    'isMulti':False,
    'default':'',
    'accessor':'',
    'read':'',
    'storable':False,
    'copyable':True,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':'',
    'uiCategory':None,
    }
),
('publisher',
    {
    'type':'drc_base',
    'isMulti':False,
    'default':'',
    'accessor':'',
    'read':'',
    'storable':False,
    'copyable':True,
    'uiEditable':Eds.Disabled,
    'uiVisible':True,
    'uiDisplay':'',
    'uiCategory':None,
    }
),
]
DrcFileProperties.extend(DrcEntryProperties)

class DrcBaseProperty(MetaProperty):

    def __init__(self, sProperty, metaobj):
        super(DrcBaseProperty, self).__init__(sProperty, metaobj)
        self.viewItems = []

    def getIconData(self):
        return self._metaobj.getIconData()

class FileTimeProperty(DrcBaseProperty):

    def read(self):
        return DrcBaseProperty.read(self).toPython()


class FileSizeProperty(DrcBaseProperty):

    def read(self):
        return MemSize(DrcBaseProperty.read(self))



class PropertyFactory(BasePropertyFactory):

    propertyTypeDct = {
    'drc_base' : DrcBaseProperty,
    'drc_time' : FileTimeProperty,
    'drc_size' : FileSizeProperty,
    }



class DrcMetaObject(MetaObject):

    propertyFactoryClass = PropertyFactory






