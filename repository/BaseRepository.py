from abc import ABC, abstractmethod
from typing import Optional

from database.connection import DBConnection
from models.PyObjectID import PyObjectID


class DBInterface(ABC):
    @abstractmethod
    async def insert_one(self, document: dict) -> str:
        pass

    @abstractmethod
    async def query(self, query: dict) -> list[dict]:
        pass

    @abstractmethod
    async def find_one(self, query: dict) -> Optional[dict]:
        pass

    @abstractmethod
    async def update_one(self, query: dict, update: dict) -> bool:
        pass

    @abstractmethod
    async def delete_one(self, query: dict) -> bool:
        pass

    @abstractmethod
    async def find_by_id(
        self, id: str | PyObjectID, query: Optional[dict]
    ) -> Optional[dict]:
        pass


class BaseRepository(DBInterface):

    def __init__(self, collection: str, db: DBConnection):
        self._collection = db.get_collection(collection)

    async def insert_one(self, document: dict) -> str:
        insertion_result = await self._collection.insert_one(document)
        return str(insertion_result.inserted_id)

    async def query(self, query: dict) -> list[dict]:
        return await self._collection.find(query).to_list(length=1000)

    async def find_one(self, query: dict) -> Optional[dict]:
        return await self._collection.find_one(query)  # type: ignore

    async def update_one(self, query: dict, update: dict) -> bool:
        result = await self._collection.update_one(query, update)
        return result.modified_count > 0

    async def delete_one(self, query: dict) -> bool:
        result = await self._collection.delete_one(query)
        return result.deleted_count > 0

    async def find_by_id(self, id: str | PyObjectID, query: dict | None) -> dict | None:
        query = query or {}

        if isinstance(id, str):
            id = PyObjectID(id)

        query["_id"] = id

        return await self._collection.find_one(query)  # type: ignore
