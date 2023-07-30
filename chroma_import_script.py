import motor.motor_asyncio

from config import env_config
from text.chroma_client import chroma_client
from text.TextSplitter import TextSplitter
from text.VectorStore import VectorStore

CONN_STRING = env_config.MONGO_DB_CONNECTION
CHROMA_PORT = env_config.CHROMA_PORT
CHROMA_HOST = env_config.CHROMA_HOST


async def main():
    client = motor.motor_asyncio.AsyncIOMotorClient(CONN_STRING)
    db = client["spacey"]
    collection = "webContent"

    web_content = db[collection]
    web_content_entries = await web_content.find({}).to_list(length=1000)

    ts = TextSplitter(1000, 70)
    vs = VectorStore(ts, chroma_client)

    documents = [
        web_content_entrie["content"] for web_content_entrie in web_content_entries
    ]

    metadata = [
        {"source_id": str(entry["_id"]), "user_id": entry["user_id"]}
        for entry in web_content_entries
    ]

    vs.add_documents(documents, metadata)  # type: ignore

    collection = chroma_client.get_collection(name="webContent")

    print(f"Imported {collection.count()} documents!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
