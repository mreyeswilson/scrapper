from models.clase import Clase
import pymongo
import os
from bson import json_util
from log import logger
from controllers.provider import Provider
from models.user import User
from datetime import timedelta, datetime

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
    
    def get_user_by_code(self, code) -> User:
        col = self.db["users"]
        result = col.find_one({ "code": code })
        if result:
            return User(**result)
        
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
        print(json_util.dumps([clase.as_dict() for clase in classes]))
        return classes
