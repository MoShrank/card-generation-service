from datetime import datetime

from bson.objectid import ObjectId
from pydantic import BaseModel, Field

from models.PyObjectID import PyObjectID


class MongoModel(BaseModel):
    id: PyObjectID = Field(default_factory=PyObjectID, alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    edited_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
