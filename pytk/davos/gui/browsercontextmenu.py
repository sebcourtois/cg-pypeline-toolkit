

from pytk.core.itemviews.basecontextmenu import BaseContextMenu

class BrowserContextMenu(BaseContextMenu):

    def __init__(self, parentView):
        super(BrowserContextMenu, self).__init__(parentView)

    def getActionSelection(self):

        view = self.view
        model = view.model()

        selectedItems = BaseContextMenu.getActionSelection(self)
        if not selectedItems:
            viewRootItem = model.itemFromIndex(view.rootIndex())
            if viewRootItem:
                selectedItems.append(viewRootItem)

        return selectedItems

    def getActionsConfig(self):

        # proj = self.model().metamodel

        actionsCfg = (
            { "label":"Edit"        , "fnc":self.editFile                            , "menu": "Main"},
            { "label":"separator"                                                    , "menu": "Main"},

            # { "label":"separator"  , "dev":False                                    , "menu": "Main"},
            { "label":"Refresh"     , "fnc":self.refreshItems                        , "menu": "Main" },
        )

        return actionsCfg

    def editFile(self, *itemList):

        drcFile = itemList[-1]._metaobj

        drcFile.makePrivateCopy(dry_run=True)

    editFile.auth_types = ("DrcFile",)

    def refreshItems(self, *itemList):

        itemList[-1].refreshRow()


