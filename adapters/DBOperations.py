from typing import Optional

from adapters.database_models.PyObjectID import PyObjectID
from adapters.DBConnection import DBConnection
from adapters.DBInterface import DBInterface


class DBOperations(DBInterface):
    def __init__(self, collection: str, db: DBConnection):
        self._collection = db.get_collection(collection)

    async def insert_one(self, document: dict) -> str:
        result = await self._collection.insert_one(document)
        return str(result.inserted_id)

    async def query(self, query: dict) -> list[dict]:
        return await self._collection.find(query).to_list(length=1000)

    async def find_one(self, query: dict) -> Optional[dict]:
        return await self._collection.find_one(query)  # type: ignore

    async def update_one(self, query, update: dict) -> bool:
        result = await self._collection.update_one(query, update)
        return result.modified_count > 0

    async def delete_one(self, query) -> bool:
        result = await self._collection.delete_one(query)
        return result.deleted_count > 0

    async def find_by_id(
        self, id: str | PyObjectID, query: dict | None
    ) -> Optional[dict]:
        query = query or {}

        if isinstance(id, str):
            id = PyObjectID(id)

        query["_id"] = id

        return await self._collection.find_one(query)  # type: ignore
