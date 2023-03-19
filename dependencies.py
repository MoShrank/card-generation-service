from typing import Optional

from config import env_config
from database.db import DBConnection, DBOperations
from external.CardGeneration import (
    CardGenerationInterface,
    CardGenerationMock,
)
from external.DeckServiceAPI import DeckServiceAPI
from models.ModelConfig import ModelConfig

NOTES_COLLECTION = "note"
USER_COLLECTION = "openaiUser"
OPENAI_CONFIG_COLLECTION = "modelConfig"
WEBCONTENT_COLLECTION = "webContent"

db_connection = DBConnection(env_config.DATABASE)

note_repo = DBOperations(NOTES_COLLECTION, db_connection)
user_repo = DBOperations(USER_COLLECTION, db_connection)
web_content_repo = DBOperations(WEBCONTENT_COLLECTION, db_connection)
config_repo = DBOperations(OPENAI_CONFIG_COLLECTION, db_connection)

model_config: Optional[ModelConfig] = None
card_generation: Optional[CardGenerationInterface] = None

deck_service = DeckServiceAPI(env_config)


def get_note_repo():
    return note_repo


def get_user_repo():
    return user_repo


def get_web_content_repo():
    return web_content_repo


def get_card_generation():
    return card_generation


def get_deck_service():
    return deck_service


def get_model_config():
    return model_config
