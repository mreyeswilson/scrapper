from datetime import datetime
from enum import Enum

from bson.objectid import ObjectId


class ClassStatus(Enum):
    CANCELLED = "Cancelada"
    NOT_CANCELLED = "No Cancelada"


class Clase:

    link = ""

    def __init__(self, id, title, start, url, color, _id=None, event_id=None, link=None, attendance=None):
        self._id = _id or ObjectId()
        self.id = id
        self.title = title
        self.start = start
        self.url = url
        self.color = color
        self.event_id = event_id
        self.link = link
        self.attendance = attendance

    def as_dict(self):
        return {
            "_id": self._id,
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "color": self.color,
            "start": self.start,
            "event_id": self.event_id,
            "link": self.link,
            "attendance": self.attendance
        }

    def is_today(self, day=0):
        return datetime.strptime(self.start, '%Y-%m-%dT%H:%M').date() == day.date()

    def after(self, hour=0):
        return datetime.strptime(self.start, '%Y-%m-%dT%H:%M').hour > hour

    @property
    def fecha(self):
        return self.start.date()

    @property
    def hora(self):
        return self.start.time()
