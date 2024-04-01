import motor.motor_asyncio

from adapters.vector_store.ChromaConnection import chroma_conn
from adapters.vector_store.VectorStore import VectorStore
from config import env_config
from lib.TextSplitter import TextSplitter

CONN_STRING = env_config.MONGO_DB_CONNECTION
CHROMA_PORT = env_config.CHROMA_PORT
CHROMA_HOST = env_config.CHROMA_HOST

CHROMA_COLLECTION_NAME = "content"
MONGO_TARGET_COLLECTION = "content"


async def main():
    # --- Connect to MongoDB and ChromaDB --- #
    db_client = motor.motor_asyncio.AsyncIOMotorClient(CONN_STRING)
    chroma_client = chroma_conn.get_client()
    db = db_client["spacey"]
    target_collection = db[MONGO_TARGET_COLLECTION]
    chroma_collection = chroma_client.get_or_create_collection(name="content")

    ts = TextSplitter(1000, 70)
    vs = VectorStore(ts, chroma_client)
    no_docs = await target_collection.count_documents({})

    if no_docs <= 0:
        web_content_collection = "webContent"
        pdf_collection_name = "pdf"

        # --- Get all web content and pdf entries --- #
        web_content = db[web_content_collection]
        web_content_entries = await web_content.find({}).to_list(length=1000)

        pdf = db[pdf_collection_name]
        pdf_entries = await pdf.find({}).to_list(length=1000)
        pdf_entries = [
            pdf_entry
            for pdf_entry in pdf_entries
            if pdf_entry["processing_status"] == "processed"
        ]

        # --- Migrate old collections to target collection --- #
        content = []

        for web_content_instance in web_content_entries:
            content.append(
                {
                    "user_id": web_content_instance["user_id"],
                    "title": web_content_instance["title"],
                    "summary": web_content_instance["summary"],
                    "processing_status": "processed",
                    "source_type": "url",
                    "raw_text": web_content_instance["content"],
                    "view_text": web_content_instance["content"],
                    "source": web_content_instance["url"],
                    "created_at": web_content_instance["created_at"],
                    "updated_at": web_content_instance["updated_at"],
                }
            )

        for pdf_instance in pdf_entries:
            content.append(
                {
                    "user_id": pdf_instance["user_id"],
                    "title": pdf_instance["title"],
                    "summary": pdf_instance["summary"],
                    "processing_status": "processed",
                    "source_type": "pdf",
                    "raw_text": pdf_instance["extracted_markdown"],
                    "view_text": pdf_instance["extracted_markdown"],
                    "storage_ref": pdf_instance["storage_reference"],
                    "created_at": pdf_instance["created_at"],
                    "updated_at": pdf_instance["updated_at"],
                }
            )

        await target_collection.insert_many(content)

        no_docs = await target_collection.count_documents({})
        print(f"Migrated {no_docs} documents into mongoDB!")

    if chroma_collection.count() <= 0:
        content = await target_collection.find({}).to_list(length=1000)

        documents = []
        metadata = []

        for c in content:
            if "view_text" in c and c["view_text"]:
                documents.append(c["view_text"])

                metadata.append(
                    {
                        "source_id": str(c["_id"]),
                        "user_id": c["user_id"],
                        "source_type": c["source_type"],
                    }
                )

        # --- Add all documents to ChromaDB --- #
        vs.add_documents(documents, metadata)  # type: ignore
        print(f"Imported {chroma_collection.count()} documents into chroma DB!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
