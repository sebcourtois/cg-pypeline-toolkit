
import os

from pytk.core.authenticator import Authenticator
from pytk.util.fsutils import jsonRead, jsonWrite
from pytk.util.fsutils import pathJoin

class DummyAuth(Authenticator):

    def __init__(self):
        self.authenticated = False
        self.cookieFile = pathJoin(os.getenv("USERPROFILE"),
                                   "dev_auth.json")

    def loggedUser(self, *args, **kwargs):

        if os.path.isfile(self.cookieFile):
            return jsonRead(self.cookieFile)

        return {}

    def login(self, sLogin, sPwd, **kwargs):
        userData = {"login":sLogin}
        jsonWrite(self.cookieFile, userData)
        return userData

    def logout(self, *args, **kwargs):
        if os.path.isfile(self.cookieFile):
            os.remove(self.cookieFile)