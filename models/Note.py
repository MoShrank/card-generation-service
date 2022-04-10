from typing import Dict, List

from pydantic import BaseModel, Field

from models.HttpModels import BaseResponse
from models.MongoModel import MongoModel
from models.PyObjectID import PyObjectId


class Card(BaseModel):
    question: str
    answer: str


class Cards(BaseModel):
    cards: List[Card]
    cards_added: bool
    original_cards: bool
    created_at: str


class Note(MongoModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    encoding: str
    user_id: str
    deck_id: str
    text: str
    completion: str
    cards_added: bool
    cards: List[Cards]
    created_at: str


class NotesResponse(MongoModel, BaseResponse):
    class Data(BaseModel):
        id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
        text: str
        cards: List[Card]

    data: Dict[str, Data]


class CardsResponse(MongoModel, BaseResponse):
    class Data(BaseModel):
        id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
        text: str
        cards: List[Card]

    data: Data
