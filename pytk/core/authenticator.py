
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
        if userData:
            # logMsg( "Already authenticated", log = 'info' )
            self.authenticated = True

        if not self.authenticated:
            userData = loginDialog(loginFunc=self.login)

        return userData
