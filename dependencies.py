from enum import Enum
from typing import Optional

from fastapi import Depends

from config import env_config
from database.db import DBConnection, DBOperations
from external.DeckServiceAPI import DeckServiceAPI
from models.ModelConfig import (
    ModelConfig,
    QuestionAnswerGPTConfig,
)
from text.CardSourceGenerator import CardSourceGenerator, CardSourceGeneratorMock
from text.chroma_client import chroma_client
from text.content.ContentExtractor import ContentExtractor
from text.GPT.GPTInterface import GPTInterface
from text.GPT.Summarizer import SummarizerInterface
from text.PDFStorage import PDFStorage
from text.SciPDFToMD import SciPDFToMDInterface
from text.TextSplitter import TextSplitter
from text.VectorStore import VectorStore

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


model_config: Optional[ModelConfig] = None
card_generation: Optional[GPTInterface] = None

single_flashcard_model_config: Optional[ModelConfig] = None
single_flashcard_generation: Optional[GPTInterface] = None

summarizer_model_config: Optional[ModelConfig] = None
summarizer: Optional[SummarizerInterface] = None

question_answer_gpt_config: Optional[QuestionAnswerGPTConfig] = None
question_answer_gpt: Optional[GPTInterface] = None

text_splitter = TextSplitter(1000, 70)
vector_store = VectorStore(text_splitter, chroma_client, 3)

pdf_to_md = Optional[SciPDFToMDInterface]
pdf_storage = PDFStorage(env_config)

deck_service = DeckServiceAPI(env_config)

card_source_generator = (
    CardSourceGenerator() if env_config.is_prod() else CardSourceGeneratorMock()
)

db_conn = DBConnection(env_config.DATABASE)


def get_db_connection():
    return db_conn


def get_config_repo():
    db_connection = get_db_connection()
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


def get_summarizer():
    return summarizer


def get_card_generation():
    return card_generation


def get_single_card_generation():
    return single_flashcard_generation


def get_deck_service():
    return deck_service


def get_model_config():
    return model_config


def get_card_source_generator():
    return card_source_generator


def get_question_answer_gpt():
    return question_answer_gpt


def get_vector_store():
    return vector_store


def get_pdf_to_md():
    return pdf_to_md


def get_pdf_storage():
    return pdf_storage


content_extractor = ContentExtractor()


def get_content_extractor():
    return content_extractor
