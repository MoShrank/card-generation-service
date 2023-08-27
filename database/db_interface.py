from abc import ABC, abstractmethod
from typing import Any, Dict


class DBInterface(ABC):
    @abstractmethod
    async def insert_one(self, document: Dict) -> Dict:
        pass

    @abstractmethod
    async def query(self, query: Dict) -> list[Dict]:
        pass

    @abstractmethod
    async def find_one(self, query: Dict) -> Dict:
        pass

    @abstractmethod
    async def update_one(self, query: Dict, update: Dict) -> Dict:
        pass

    @abstractmethod
    async def delete_one(self, query: Dict) -> Any:
        pass
