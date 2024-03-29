import motor.motor_asyncio

from adapters.ChromaConnection import chroma_conn
from adapters.VectorStore import VectorStore
from config import env_config
from lib.TextSplitter import TextSplitter

CONN_STRING = env_config.MONGO_DB_CONNECTION
CHROMA_PORT = env_config.CHROMA_PORT
CHROMA_HOST = env_config.CHROMA_HOST


async def main():
    client = motor.motor_asyncio.AsyncIOMotorClient(CONN_STRING)

    chroma_client = chroma_conn.get_client()
    db = client["spacey"]
    web_content_collection = "webContent"
    pdf_collection_name = "pdf"

    web_content = db[web_content_collection]
    web_content_entries = await web_content.find({}).to_list(length=1000)

    pdf = db[pdf_collection_name]
    pdf_entries = await pdf.find({}).to_list(length=1000)

    pdf_entries = [
        pdf_entry
        for pdf_entry in pdf_entries
        if pdf_entry["processing_status"] == "processed"
    ]

    ts = TextSplitter(1000, 70)
    vs = VectorStore(ts, chroma_client)

    documents = [
        web_content_entrie["content"] for web_content_entrie in web_content_entries
    ]

    documents.extend([pdf_entry["extracted_markdown"] for pdf_entry in pdf_entries])

    metadata = [
        {
            "source_id": str(entry["_id"]),
            "user_id": entry["user_id"],
            "source_type": "web",
        }
        for entry in web_content_entries
    ]

    metadata.extend(
        [
            {
                "source_id": str(entry["_id"]),
                "user_id": entry["user_id"],
                "source_type": "pdf",
            }
            for entry in pdf_entries
        ]
    )

    vs.add_documents(documents, metadata)  # type: ignore

    collection = chroma_client.get_collection(name="content")

    print(f"Imported {collection.count()} documents!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
