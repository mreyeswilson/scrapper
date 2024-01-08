from bson.objectid import ObjectId

class User:

    def __init__(self, code, name, profile, id, since, until, _id=None) -> None:
        self._id = _id or ObjectId()
        self.id = id
        self.code = code
        self.name = name
        self.profile = profile
        self.since = since
        self.until = until

    def as_dict(self):
        return self.__dict__
    
    @property
    def level(self):
        return self.profile.split(" ", 1)[1]