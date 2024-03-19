from datetime import datetime
from typing import Dict, List, Optional

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


class Note(MongoModel):
    id: PyObjectID = Field(default_factory=PyObjectID, alias="_id")
    user_id: str
    deck_id: str
    text: str
    cards_added: bool
    cards_edited: bool
    cards: List[Card]
    cards_edited_at: Optional[datetime]
    created_at: str


# HTTP Handler models


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
