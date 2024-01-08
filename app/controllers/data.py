import os
import re
from datetime import datetime, timedelta

import pymongo
from bson import json_util
from bson.objectid import ObjectId
from controllers.provider import Provider
from controllers.utils import Util
from log import logger
from models.clase import Clase
from models.user import User


class Data:

    def __init__(self, provider: Provider):
        self._provider = provider
        self.client = pymongo.MongoClient(os.environ["MONGO_DB_URI"])
        self.db = self.client["beprogrammer"]

    def update_classes(self):
        col = self.db["clases"]
        try:
            result = col.delete_many({})
            logger.warn(f"Item deleted: {result.deleted_count}")

            classes = self._provider.get_clases()
            classes = [clase.as_dict() for clase in classes]
            result = col.insert_many(classes)
            logger.warn(f"Items inserted: {len(result.inserted_ids)}")
            logger.info("Data updated!")
        except Exception as e:
            print(e)
            logger.error("Error saving classes")

    def create_user(self, code) -> User:
        col = self.db["users"]
        try:
            usr = self._provider.autenticate(code).get_profile()
            col.insert_one(usr.as_dict())
            return usr
        except Exception as e:
            raise Exception(e)

    def get_users(self) -> list[User]:
        col = self.db["users"]
        cursor = col.find({})
        return [User(**usr) for usr in cursor]

    def get_user_by_code(self, code) -> User:
        col = self.db["users"]
        result = col.find_one({"code": code})
        if result:
            return User(**result)

    def get_oral_test_classes(self) -> list[Clase]:
        col = self.db["clases"]
        pattern = re.compile(f"^(ORAL TEST | ADULTOS)")
        results = col.find({
            "start": {
                "$gt": datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
            },
            "title": {
                "$regex": pattern
            }
        })
        classes = [Clase(**result) for result in results]
        # print(json_util.dumps([clase.as_dict() for clase in classes]))
        return classes

    def get_clases_by_date(self, date: datetime, type):
        col = self.db["clases"]
        results = col.find({
            "start": {
                "$gte": date,
                "$lt": date.replace(hour=0, minute=0, second=0) + timedelta(days=1)
            },
            "title": {
                "$regex": type
            }
        })

        classes = [Clase(**result) for result in results]
        # print(json_util.dumps([clase.as_dict() for clase in classes]))
        return classes

    def get_schedule(self, id, week=None, all=False):
        filter = {
            "user": id,
        }
        col = self.db["schedule"]

        if not all:
            if week is None:
                week = datetime.now().isocalendar().week
            filter.update({"week": week})
            return col.find_one(filter)
        return [sch for sch in col.find(filter)]
    
    def get_class_by_id(self, id):
        col = self.db["classes"]
        return col.find_one({
            "id": id,
        })

    def save_programmed_clases(self, clases: list[Clase], usr):
        col = self.db["schedule"]
        next_moday = Util.get_next_monday()
        week = next_moday.isocalendar().week

        obj = {}
        obj["user"] = usr.id
        obj["week"] = week
        obj["classes"] = []

        for clase in clases:
            obj["classes"].append({
                "id": clase.id,
                "event_id": clase.event_id,
                "attendance": {}
            })

        col.update_one({"week": week}, {
            "$set": obj
        }, True)

    def get_week_classes(self, week, user_id):
        col = self.db["schedule"]
        return col.find_one({"week": week, "user": user_id})

    def update_schedule(self, schedule):
        col = self.db["schedule"]
        col.update_one({"_id": ObjectId(schedule["_id"])}, {
            "$set": schedule
        })

    def update_profile(self):
        col = self.db["users"]
        for user in col.find({}):
            self._provider.autenticate(user["code"])
            usr = self._provider.get_profile()
            col.find_one_and_update({
                "code": usr.code
            }, {
                "$set": {
                    "profile": usr.profile
                }
            })
            logger.info("Perfil actualizado!")