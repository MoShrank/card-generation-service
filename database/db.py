import logging
from typing import Dict

import motor.motor_asyncio

from config import env_config
from database.db_interface import DBInterface

logger = logging.getLogger(__name__)


class DBConnection:
    MAX_CONNECTION_TIME = 5000

    def __init__(self, db_name: str):
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(
                env_config.MONGO_DB_CONNECTION,
                serverSelectionTimeoutMS=self.MAX_CONNECTION_TIME,
            )
            self._db = client[db_name]
        except Exception as e:
            logger.error("MongoDB connection error!")
            raise Exception("MongoDB connection error!", e)

    async def wait_for_connection(self):
        try:
            await self._db.command("ismaster")
        except Exception as e:
            logger.error("MongoDB connection error!")
            raise Exception("MongoDB connection error!", e)

    def get_db(self) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        return self._db

    def get_collection(
        self, collection: str
    ) -> motor.motor_asyncio.AsyncIOMotorCollection:
        return self._db[collection]


class DBOperations(DBInterface):
    def __init__(self, collection: str, db: DBConnection):
        self._collection = db.get_collection(collection)

    async def insert_one(self, document: Dict):
        return await self._collection.insert_one(document)

    async def query(self, query: Dict):
        return await self._collection.find(query).to_list(length=1000)

    async def find_one(self, query: Dict):
        return await self._collection.find_one(query)

    async def update_one(self, query, update: Dict):
        return await self._collection.update_one(query, update)

    async def delete_one(self, query):
        return await self._collection.delete_one(query)
