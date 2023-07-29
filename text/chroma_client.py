import asyncio

import chromadb  # type: ignore

from config import env_config

is_dev = env_config.is_dev()

if is_dev:
    chroma_client = chromadb.EphemeralClient()
else:
    chroma_client = chromadb.HttpClient(
        host=env_config.CHROMA_HOST, port=env_config.CHROMA_PORT
    )


async def import_data():
    collection = chroma_client.get_collection("webContent")

    if collection.count() <= 0:
        from chroma_import_script import main

        try:
            await main()
        except Exception as e:
            print(f"Could not import chromaDB data from mongoDB. Error: {e}")
    else:
        print("Nothing to import...")


async def wait_for_chroma_connection(timeout_seconds):
    start_time = asyncio.get_event_loop().time()

    while True:
        heartbeat = chroma_client.heartbeat()

        if heartbeat:
            return heartbeat

        elapsed_time = asyncio.get_event_loop().time() - start_time
        if elapsed_time >= timeout_seconds:
            raise TimeoutError(
                "Timed out while waiting for Chroma database connection."
            )

        await asyncio.sleep(0.5)
