from abc import ABC, abstractmethod
from typing import Optional

from adapters.database_models.PyObjectID import PyObjectID


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
