from pydantic import BaseModel, Field

from models.PyObjectID import PyObjectID


class User(BaseModel):
    id: PyObjectID = Field(default_factory=PyObjectID, alias="_id")
    user_id: str
    total_no_generated: str
