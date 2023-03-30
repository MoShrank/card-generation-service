from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field

from config import env_config
from models.HttpModels import BaseResponse
from models.MongoModel import MongoModel
from models.PyObjectID import PyObjectID


class GPTCard(BaseModel):
    question: str = Field(min_length=1, strip_whitespace=True)
    answer: str = Field(min_length=1, strip_whitespace=True)


# MongoDB models
class Card(GPTCard):
    source_start_index: int
    source_end_index: int


class Cards(BaseModel):
    cards: List[Card]
    cards_added: bool
    original_cards: bool
    created_at: datetime


class Note(MongoModel):
    id: PyObjectID = Field(default_factory=PyObjectID, alias="_id")
    user_id: str
    deck_id: str
    text: str
    cards_added: bool
    cards: List[Cards]
    created_at: datetime


# HTTP Handler models
class NoteResponse(BaseResponse):
    class Data(BaseModel):
        id: str
        cards: List[Card]

    data: Data


class NotesResponse(BaseResponse):
    class Data(BaseModel):
        id: str
        text: str
        cards: List[Card]

    data: Dict[str, Data]


class GenerateCardsRequest(BaseModel):
    text: str = Field(max_length=env_config.MAX_TEXT_LENGTH, strip_whitespace=True)
    deck_id: str


class CardsResponse(BaseResponse):
    class Data(BaseModel):
        id: str
        text: str
        cards: List[Card]

    data: Data


class UpdatedCardsResponse(BaseResponse):
    class Data(BaseModel):
        cards: List[Card]

    data: Data


class UpdateCardsRequest(BaseModel):
    cards: List[Card]


class DeckServiceCard(BaseModel):
    id: str
    question: str
    answer: str
    deck_id: str = Field(default=(...), alias="deckID")


class AddedCardsResponse(BaseResponse):
    class Data(BaseModel):
        cards: List[DeckServiceCard]

    data: Data
