from pydantic import BaseModel, Field

from models.PyObjectID import PyObjectID


class ModelParameters(BaseModel):
    temperature: int
    engine: str
    max_tokens: int
    top_p: int
    n: int
    stop_sequence: str


class ModelConfig(BaseModel):
    id: PyObjectID = Field(default_factory=PyObjectID, alias="_id")
    description: str
    parameters: ModelParameters
