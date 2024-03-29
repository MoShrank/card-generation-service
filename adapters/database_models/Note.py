from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from adapters.database_models.BaseMongoModel import BaseMongoModel


class GPTCard(BaseModel):
    question: str = Field(min_length=1, strip_whitespace=True)
    answer: str = Field(min_length=1, strip_whitespace=True)


class Card(GPTCard):
    source_start_index: int
    source_end_index: int


class Note(BaseMongoModel):
    user_id: str
    deck_id: str
    text: str
    cards_added: bool
    cards_edited: bool
    cards: list[Card]
    cards_edited_at: Optional[datetime]
