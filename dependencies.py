from adapters.DeckServiceAPI import DeckServiceAPI
from config import env_config
from lib.CardSourceGenerator import CardSourceGenerator, CardSourceGeneratorMock

deck_service = DeckServiceAPI(env_config)

card_source_generator = (
    CardSourceGenerator() if env_config.is_prod() else CardSourceGeneratorMock()
)


def get_deck_service():
    return deck_service


def get_card_source_generator():
    return card_source_generator
