from datetime import datetime
from bson.objectid import ObjectId

class Clase:

    link = ""
    def __init__(self, id, title, start, url, color, _id = None):
        self._id = _id or ObjectId()
        self.id = id
        self.title = title
        self.start = start
        self.url = url
        self.color = color


    def as_dict(self):
        return {
            "_id": self._id,
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "color": self.color,
            "start": self.start,
        }
        


    def is_today(self, day=0):
        return datetime.strptime(self.start, '%Y-%m-%dT%H:%M').date() == day.date()

    def after(self, hour=0):
        return datetime.strptime(self.start, '%Y-%m-%dT%H:%M').hour > hour
