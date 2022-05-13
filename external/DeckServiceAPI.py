from abc import ABC, abstractmethod
from typing import List

import requests
from config import EnvConfig
from models.Note import Card, DeckServiceCard


class DeckServiceAPIInterface(ABC):
    @abstractmethod
    def save_cards(self, user_id: str, deck_id: str, cards: List[Card]):
        pass


class DeckServiceAPI(DeckServiceAPIInterface):
    def __init__(self, config: EnvConfig):
        self.DECK_SERVICE_HOST_NAME = config.DECK_SERVICE_HOST_NAME

    def save_cards(
        self, user_id: str, deck_id: str, cards: List[Card]
    ) -> List[DeckServiceCard]:
        url = f"http://{self.DECK_SERVICE_HOST_NAME}/decks/{deck_id}/cards?userID={user_id}"
        data = [{"deckID": deck_id, **card} for card in cards]

        response = requests.post(url, json=data)

        if response.status_code != 201:
            raise Exception(
                f"Failed to save cards. Status code: {response.status_code}. Response: {response.json()}"
            )

        response_body = response.json()
        response_data: List[DeckServiceCard] = response_body["data"]

        return response_data
