from config import env_config
from database.db import DBConnection, DBOperations
from external.CardGenerationAPI import CardGenerationAPI, CardGenerationAPIMock
from external.DeckServiceAPI import DeckServiceAPI

NOTES_COLLECTION = "note"
USER_COLLECTION = "openaiUser"
OPENAI_CONFIG_COLLECTION = "modelConfig"

db_connection = DBConnection(env_config.DATABASE)

note_repo = DBOperations(NOTES_COLLECTION, db_connection)
user_repo = DBOperations(USER_COLLECTION, db_connection)
config_repo = DBOperations(OPENAI_CONFIG_COLLECTION, db_connection)

model_config = None

deck_service = DeckServiceAPI(env_config)

if env_config.ENV == "development":
    card_generation_api = CardGenerationAPIMock()
else:
    card_generation_api = CardGenerationAPI(env_config)


def get_note_repo():
    return note_repo


def get_user_repo():
    return user_repo


def get_card_generation_api():
    return card_generation_api


def get_deck_service():
    return deck_service


def get_model_config():
    return model_config
