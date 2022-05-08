from abc import ABC, abstractmethod
from typing import List

import requests
from config import EnvConfig
from models.Note import Card


class DeckServiceAPIInterface(ABC):
    @abstractmethod
    def save_cards(self, user_id: str, deck_id: str, cards: List[Card]):
        pass


class DeckServiceAPI(DeckServiceAPIInterface):
    def __init__(self, config: EnvConfig):
        self.DECK_SERVICE_HOST_NAME = config.DECK_SERVICE_HOST_NAME

    def save_cards(self, user_id: str, deck_id: str, cards: List[Card]):
        url = f"{self.DECK_SERVICE_HOST_NAME}/card"
        data = {"user_id": user_id, "deck_id": deck_id, "cards": cards}

        response = requests.post(url, json=data)

        if response.status_code != 200:
            raise Exception("Failed to save cards")

        return response.json()
