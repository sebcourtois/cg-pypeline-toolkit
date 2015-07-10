
from getpass import getpass

from pytk.util.sysutils import isQtApp
from .dialogs import loginDialog


class Authenticator(object):

    def __init__(self):
        self.authenticated = False

    def loggedUser(self, *args, **kwargs):
        return {}

    def login(self, *args, **kwargs):
        return {}

    def logout(self, *args, **kwargs):
        return

    def authenticate(self, **kwargs):

        if kwargs.get('relog', False):
            self.logout()

        userData = self.loggedUser()
        if not userData:

            if isQtApp():
                userData = loginDialog(loginFunc=self.login)
            else:
                for _ in xrange(2):
                    sUser = raw_input("login:")
                    sPwd = getpass()
                    userData = self.login(sUser, sPwd)
                    if userData:
                        break

        if userData:
            self.authenticated = True

        return userData
