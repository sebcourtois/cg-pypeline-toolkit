
import functools

from PySide import QtGui

from pytk.core.itemviews.utils import createAction
from pytk.util.logutils import logMsg

class BaseContextMenu(QtGui.QMenu):

    def __init__(self, parentView):
        super(BaseContextMenu, self).__init__(parentView)

        self.view = parentView
        self.actionSelection = []
        self.actionSelectionLoaded = False

        self.createActions()
        self.buildSubmenus()

    def model(self):
        return self.view.model()

    def getActionSelection(self):

        selectedItems = self.view.selectionModel().selectedItems[:]

        if selectedItems:
            currentItems = self.model().itemFromIndex(self.view.currentIndex())
            if currentItems:

                try: selectedItems.remove(currentItems)
                except ValueError: pass

                selectedItems.append(currentItems)

        return selectedItems

    def loadActionSelection(self):

        self.actionSelection = self.getActionSelection()
        self.actionSelectionLoaded = True

    def assertActionSelection(self):

        if not self.actionSelectionLoaded:
            raise RuntimeError, "Action Selection not loaded."
        else:
            self.actionSelectionLoaded = False

    def launchAction(self, actionDct, checked):

        self.assertActionSelection()

        try:
            logMsg('# Action: "{0}" > "{1}" #'.format(actionDct["menu"], actionDct["label"]))
        except Exception, e:
            logMsg(e, warning=True)

        args = actionDct.get("args", []) + self.actionSelection
        kwargs = actionDct.get("kwargs", {})
        return actionDct["fnc"](*args, **kwargs)

    def getActionsConfig(self):
        return []

    def createActions(self):

        self.createdActions = []
        self.createdActionConfigs = []

        for actionDct in self.getActionsConfig():
            sAction = actionDct["label"]
            sMenu = actionDct.get("menu", "Main")

#            if actionDct.get("dev", False):
#                if not cmnCfg.isDevEnabled():
#                    continue

            if sAction == "separator":
                qAction = None
            else:
                fnc = functools.partial(self.launchAction, actionDct)
                qAction = createAction(sAction, self, slot=fnc)

                self.createdActions.append(qAction)

            actionDct["action"] = qAction
            actionDct["menu"] = sMenu

            self.createdActionConfigs.append(actionDct)

    def buildSubmenus(self):

        qMenuDct = { "Main": self }
        for actionDct in self.createdActionConfigs:

            sMenu = actionDct["menu"]
            qAction = actionDct["action"]

            qMenu = qMenuDct.get(sMenu, None)
            if qMenu is None:
                qMenu = self.addMenu(sMenu)
                qMenuDct[sMenu] = qMenu

            if qAction is None:
                qMenu.addSeparator()
            else:
                qMenu.addAction(qAction)

        del qMenuDct["Main"]
        return qMenuDct

    def yieldAllowedActions(self, leaf):

        for actionDct in self.createdActionConfigs:

            qAction = actionDct["action"]
            if qAction is None:
                continue

            fnc = actionDct["fnc"]
            allowedTypes = getattr(fnc, "auth_types", None)
            if not allowedTypes:
                yield qAction
            elif type(leaf).__name__ in allowedTypes:
                yield qAction

    def updateVisibilities(self):

        if not self.actionSelection:
            return

        allowedActions = set(self.createdActions)
        for leaf in self.actionSelection:
            allowedActions.intersection_update(self.yieldAllowedActions(leaf))

        if not allowedActions:
            return

        for qAction in self.createdActions:
            qAction.setVisible((qAction in allowedActions))

        for qMenu in self.findChildren(QtGui.QMenu):
            qMenu.menuAction().setVisible(not qMenu.isEmpty())

    def launch(self, event):
        self.loadActionSelection()
        self.updateVisibilities()
        self.exec_(event.globalPos())