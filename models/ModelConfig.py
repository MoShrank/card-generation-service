from typing import Any, Callable, List, Literal, Optional

from pydantic import BaseModel, Field, validator

from models.Note import GPTCard
from models.PyObjectID import PyObjectID


def create_contains_placeholders_validator(
    *placeholders: str,
) -> Callable[[Any, Any], Any]:
    def _validator(cls, v):
        """
        Validate that string contains all specified placeholders.
        """
        for placeholder in placeholders:
            if f"{{{placeholder}}}" not in v:
                raise ValueError(f'String must contain a "{placeholder}" placeholder')
        return v

    return _validator


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
    stop_sequence: Optional[List[str]]


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


class QuestionAnswerGPTConfig(ModelConfig):
    system_message: str

    @validator("system_message", allow_reuse=True)
    def system_message_contains_placeholders(cls, v):
        return create_contains_placeholders_validator("question")(cls, v)
