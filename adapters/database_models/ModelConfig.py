from typing import Any, Callable, List, Literal, Optional

from pydantic import BaseModel, Field, validator

from adapters.database_models.PyObjectID import PyObjectID


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


class GPTCard(BaseModel):
    question: str
    answer: str


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
    system_message: str


class QuestionAnswerGPTConfig(ModelConfig):
    @validator("system_message", allow_reuse=True)
    def system_message_contains_placeholders(cls, v):
        return create_contains_placeholders_validator("question")(cls, v)
