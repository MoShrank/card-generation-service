from typing import Dict

import motor.motor_asyncio
from config import env_config

from database.db_interface import DBInterface


class DB(DBInterface):
    NOTES_COLLECTION = "notes"
    MAX_CONNECTION_TIME = 5

    def __init__(self):
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(
                env_config.MONGO_DB_CONNECTION, connectTimeoutMS=5000
            )
            client.server_info()
        except Exception as e:
            raise Exception("MongoDB connection error!", e)

        self._db = client["spacey"]
        self._collection = self._db[self.NOTES_COLLECTION]

    async def insert_one(self, document: Dict):
        return await self._collection.insert_one(document)

    async def query(self, query: Dict):
        return await self._collection.find(query).to_list(length=1000)

    async def find_one(self, query: Dict):
        return await self._collection.find_one(query)

    async def update_one(self, id: str, document: Dict):
        return await self._collection.update_one({"_id": id}, {"$set": document})
