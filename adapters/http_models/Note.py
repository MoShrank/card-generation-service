from typing import Dict, List

from pydantic import BaseModel, Field

from adapters.database_models.Note import Card
from config import env_config
from adapters.http_models.HttpModels import BaseResponse



class NoteResponseData(BaseModel):
    id: str
    cards: List[Card]


NoteResponse = BaseResponse[NoteResponseData]


class NotesResponseData(BaseModel):
    id: str
    text: str
    cards: List[Card]


NotesResponse = BaseResponse[Dict[str, NotesResponseData]]


class GenerateCardsRequest(BaseModel):
    text: str = Field(max_length=env_config.MAX_TEXT_LENGTH, strip_whitespace=True)
    deck_id: str


class GenerateCardRequest(GenerateCardsRequest):
    source_start_index: int
    source_end_index: int


class CardsResponseData(BaseModel):
    id: str
    text: str
    cards: List[Card]


CardsResponse = BaseResponse[CardsResponseData]


class CardResponseData(BaseModel):
    id: str
    text: str
    card: Card


CardResponse = BaseResponse[CardResponseData]


class UpdatedCardsResponseData(BaseModel):
    cards: List[Card]


UpdatedCardsResponse = BaseResponse[UpdatedCardsResponseData]


class UpdateCardsRequest(BaseModel):
    cards: List[Card]


class DeckServiceCard(BaseModel):
    id: str
    question: str
    answer: str
    deck_id: str = Field(default=(...), alias="deckID")


class AddedCardsResponseData(BaseModel):
    cards: List[DeckServiceCard]


AddedCardsResponse = BaseResponse[AddedCardsResponseData]
