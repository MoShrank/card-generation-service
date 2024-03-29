from enum import Enum
from typing import Annotated, Optional

from fastapi import Depends

from adapters.ChromaConnection import chroma_conn
from adapters.DBConnection import DBConnection, get_db_connection
from adapters.DBOperations import DBOperations
from adapters.DeckServiceAPI import DeckServiceAPI
from adapters.PDFStorage import PDFStorage
from adapters.SciPDFToMD import SciPDFToMDInterface
from adapters.VectorStore import VectorStore
from config import env_config
from lib.CardSourceGenerator import CardSourceGenerator, CardSourceGeneratorMock
from lib.content.ContentExtractor import ContentExtractor
from lib.TextSplitter import TextSplitter

NOTES_COLLECTION = "note"
USER_COLLECTION = "openaiUser"
OPENAI_CONFIG_COLLECTION = "modelConfig"
WEBCONTENT_COLLECTION = "webContent"
PDF_COLLECTION = "pdf"


class Collections(Enum):
    NOTES = NOTES_COLLECTION
    USER = USER_COLLECTION
    OPENAI_CONFIG = OPENAI_CONFIG_COLLECTION
    WEBCONTENT = WEBCONTENT_COLLECTION
    PDF = PDF_COLLECTION


text_splitter = TextSplitter(1000, 70)
vector_store = VectorStore(text_splitter, chroma_conn.get_client(), 3)

pdf_to_md = Optional[SciPDFToMDInterface]
pdf_storage = PDFStorage(env_config)

deck_service = DeckServiceAPI(env_config)

card_source_generator = (
    CardSourceGenerator() if env_config.is_prod() else CardSourceGeneratorMock()
)


def get_config_repo(db_connection: Annotated[DBConnection, Depends()]):
    return DBOperations(OPENAI_CONFIG_COLLECTION, db_connection)


def get_note_repo(db_connection: DBConnection = Depends(get_db_connection)):
    return DBOperations(NOTES_COLLECTION, db_connection)


def get_user_repo(db_connection: DBConnection = Depends(get_db_connection)):
    return DBOperations(USER_COLLECTION, db_connection)


def get_web_content_repo(db_connection: DBConnection = Depends(get_db_connection)):
    return DBOperations(WEBCONTENT_COLLECTION, db_connection)


def get_repo(collection: str):
    def repo(db_connection: DBConnection = Depends(get_db_connection)):
        return DBOperations(collection, db_connection)

    return repo


def get_deck_service():
    return deck_service


def get_card_source_generator():
    return card_source_generator


def get_vector_store():
    return vector_store


def get_pdf_to_md():
    return pdf_to_md


def get_pdf_storage():
    return pdf_storage


content_extractor = ContentExtractor()


def get_content_extractor():
    return content_extractor
