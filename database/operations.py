from database.connection import DBConnection
from database.db_interface import DBInterface
from models.PyObjectID import PyObjectID


from typing import Dict


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

    async def find_by_id(self, id: str | PyObjectID, query: dict | None):
        query = query or {}

        if isinstance(id, str):
            id = PyObjectID(id)

        query["_id"] = id

        return await self._collection.find_one(query)