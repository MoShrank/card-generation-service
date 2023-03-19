from typing import List

from pydantic import BaseModel, Field

from models.Note import Card
from models.PyObjectID import PyObjectID


class Example(BaseModel):
    note: str
    cards: List[Card]


class ModelParameters(BaseModel):
    temperature: int
    model: str
    max_tokens: int
    top_p: int
    n: int
    stop_sequence: List[str]


class ModelConfig(BaseModel):
    id: PyObjectID = Field(default_factory=PyObjectID, alias="_id")
    type: str
    parameters: ModelParameters
    examples: List[Example]
    card_prefix: str
    note_prefix: str
    prompt_prefix: str
