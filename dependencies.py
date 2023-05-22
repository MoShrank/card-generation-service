from typing import Optional

from fastapi import Depends

from config import env_config
from database.db import DBConnection, DBOperations
from external.CardGeneration import (
    CardGenerationInterface,
)
from external.DeckServiceAPI import DeckServiceAPI
from models.ModelConfig import CardGenerationConfig, SummarizerConfig
from text.CardSourceGenerator import CardSourceGenerator, CardSourceGeneratorMock
from text.Summarizer import SummarizerInterface

NOTES_COLLECTION = "note"
USER_COLLECTION = "openaiUser"
OPENAI_CONFIG_COLLECTION = "modelConfig"
WEBCONTENT_COLLECTION = "webContent"

model_config: Optional[CardGenerationConfig] = None
card_generation: Optional[CardGenerationInterface] = None

summarizer_model_config: Optional[SummarizerConfig] = None
summarizer: Optional[SummarizerInterface] = None

deck_service = DeckServiceAPI(env_config)

card_source_generator = (
    CardSourceGenerator()
    if env_config.ENV == "production"
    else CardSourceGeneratorMock()
)


def get_db_connection():
    return DBConnection(env_config.DATABASE)


def get_config_repo():
    db_connection = DBConnection(env_config.DATABASE)
    return DBOperations(OPENAI_CONFIG_COLLECTION, db_connection)


def get_note_repo(db_connection: DBConnection = Depends(get_db_connection)):
    return DBOperations(NOTES_COLLECTION, db_connection)


def get_user_repo(db_connection: DBConnection = Depends(get_db_connection)):
    return DBOperations(USER_COLLECTION, db_connection)


def get_web_content_repo(db_connection: DBConnection = Depends(get_db_connection)):
    return DBOperations(WEBCONTENT_COLLECTION, db_connection)


def get_summarizer():
    return summarizer


def get_card_generation():
    return card_generation


def get_deck_service():
    return deck_service


def get_model_config():
    return model_config


def get_card_source_generator():
    return card_source_generator
