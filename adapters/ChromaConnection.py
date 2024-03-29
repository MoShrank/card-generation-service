import asyncio
from typing import Optional

import chromadb
from chromadb.api import ClientAPI

from config import env_config


class ChromaConnection:
    _client: ClientAPI

    def __init__(self):
        if env_config.is_dev():
            self._chroma_client = chromadb.EphemeralClient()
        else:
            self._chroma_client = chromadb.HttpClient(
                host=env_config.CHROMA_HOST, port=env_config.CHROMA_PORT
            )

    async def import_data(self, collection_name: str) -> None:
        collection = self._chroma_client.get_collection(collection_name)

        if collection.count() <= 0:
            from chroma_import_script import main

            try:
                await main()
            except Exception as e:
                print(f"Could not import chromaDB data from mongoDB. Error: {e}")
        else:
            print("Nothing to import...")

    async def wait_for_connection(self, timeout_seconds: int = 5) -> Optional[int]:
        start_time = asyncio.get_event_loop().time()

        while True:
            heartbeat = self._chroma_client.heartbeat()

            if heartbeat:
                return heartbeat

            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time >= timeout_seconds:
                raise TimeoutError(
                    "Timed out while waiting for Chroma database connection."
                )

            await asyncio.sleep(0.5)

    def get_client(self) -> ClientAPI:
        return self._chroma_client


chroma_conn = ChromaConnection()


def get_chroma_client():
    return chroma_conn
