from bson.objectid import ObjectId
from pydantic import BaseModel


class MongoModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
