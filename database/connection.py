import logging

import motor.motor_asyncio

from config import env_config

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


db_conn = DBConnection(env_config.DATABASE)


def get_db_connection():
    return db_conn
