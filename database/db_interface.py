from abc import ABC, abstractmethod
from typing import Dict


class DBInterface(ABC):
    @abstractmethod
    async def insert_one(self, document: Dict):
        pass

    @abstractmethod
    async def query(self, query: Dict):
        pass

    @abstractmethod
    async def find_one(self, query: Dict):
        pass

    @abstractmethod
    async def update_one(self, id: str, document: Dict):
        pass
