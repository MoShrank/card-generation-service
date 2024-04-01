from abc import ABC, abstractmethod
from typing import Optional

from bson import ObjectId

from adapters.database_models.PyObjectID import PyObjectID
from adapters.DBConnection import DBConnection


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

    def _doc_or_query_to_obj_id(self, query: dict) -> dict:
        if "_id" in query and isinstance(query["_id"], str):
            query["_id"] = PyObjectID(query["_id"])
        elif "id" in query and isinstance(query["id"], str):
            query["_id"] = PyObjectID(query["id"])
            del query["id"]

        return query

    def _norm_id(self, document: dict) -> dict:
        if "_id" in document:
            document["id"] = str(document["_id"])
            del document["_id"]
        elif "id" in document and isinstance(document["id"], ObjectId):
            document["id"] = str(document["id"])

        return document

    def _norm_ids(self, documents: list[dict]) -> list[dict]:
        return [self._norm_id(document) for document in documents]

    async def insert_one(self, document: dict) -> str:
        insertion_result = await self._collection.insert_one(document)
        return str(insertion_result.inserted_id)

    async def query(self, query: dict) -> list[dict]:
        query = self._doc_or_query_to_obj_id(query)
        result = await self._collection.find(query).to_list(length=1000)
        return self._norm_ids(result)

    async def find_one(self, query: dict) -> Optional[dict]:
        query = self._doc_or_query_to_obj_id(query)
        result = await self._collection.find_one(query)  # type: ignore

        if result:
            result = self._norm_id(result)

        return result

    async def update_one(self, query: dict, update: dict) -> bool:
        query = self._doc_or_query_to_obj_id(query)
        result = await self._collection.update_one(query, update)
        return result.modified_count > 0

    async def delete_one(self, query: dict) -> bool:
        query = self._doc_or_query_to_obj_id(query)
        result = await self._collection.delete_one(query)
        return result.deleted_count > 0

    async def find_by_id(self, id: str | PyObjectID, query: dict | None) -> dict | None:
        query = query or {}
        query = self._doc_or_query_to_obj_id(query)

        result = await self._collection.find_one(query)  # type: ignore

        if result:
            result = self._norm_id(result)

        return result
