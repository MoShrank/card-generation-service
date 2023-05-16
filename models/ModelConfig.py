from typing import List, Literal

from pydantic import BaseModel, Field

from models.Note import GPTCard
from models.PyObjectID import PyObjectID


class Example(BaseModel):
    note: str
    cards: List[GPTCard]


class ModelParameters(BaseModel):
    temperature: int
    model: str
    max_tokens: int
    presence_penalty: int = Field(default=0)
    frequency_penalty: int = Field(default=0)
    top_p: int
    n: int
    stop_sequence: List[str]


class Message(BaseModel):
    role: Literal["user", "system", "assistant"]
    content: str


Messages = List[Message]


class ModelConfig(BaseModel):
    id: PyObjectID = Field(default_factory=PyObjectID, alias="_id")
    parameters: ModelParameters
    max_model_tokens: int


class SummarizerConfig(ModelConfig):
    system_message: str
    user_message_prefix: str


class CardGenerationConfig(ModelConfig):
    type: str
    examples: List[Example]
    card_prefix: str
    note_prefix: str
    prompt_prefix: str
