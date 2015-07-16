
class DbError(Exception):
    pass

class DbFieldError(DbError):
    pass

class DbReadError(DbError):
    pass

class DbUpdateError(DbError):
    pass

class DbSearchError(DbError):
    pass

class DbDeleteError(DbError):
    pass

class DbCreateError(DbError):
    pass

class DbNode(object):

    __slots__ = ('_db', '_rec', '_id', '_time')

    def __init__(self, db, record):

        self._id = record['_id']
        self._db = db
        self._rec = record.copy()
        self._time = record['time']

    def getValue(self, sField):

        try:
            return self._rec[sField]
        except KeyError:
            raise DbFieldError("{} has no such field: '{}'".format(self, sField))

    def setValue(self, sField, value):

        recs = self._db.update(self._id, {sField:value})
        if not recs:
            raise DbUpdateError("Failed to update {}".format(self))

        self._rec = recs[0].copy()

    def setData(self, data):

        recs = self._db.update(self._id, data)
        if not recs:
            raise DbUpdateError("Failed to update {}".format(self))

        self._rec = recs[0].copy()

    def refresh(self):

        recs = self._db.read(self._id)
        if not recs:
            raise DbReadError("Failed to read {}".format(self))

        self._rec = recs[0].copy()

    def delete(self):
        return self._db.delete(self._id)

    def __repr__(self):

        cls = self.__class__

        try:
            sRepr = ("{}('{}')".format(cls.__name__, self._id))
        except AttributeError:
            sRepr = cls.__name__

        return sRepr
