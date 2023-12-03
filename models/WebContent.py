from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, root_validator
from pydantic.fields import Field

from models.HttpModels import BaseResponse

from .PyObjectID import PyObjectID


class WebContent(BaseModel):
    id: PyObjectID = Field(default_factory=PyObjectID, alias="_id")
    name: str
    user_id: str
    url: str
    title: str
    content: str
    html: str
    summary: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class WebContentResponseData(BaseModel):
    id: str
    name: str
    url: str
    summary: Optional[str]
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda oid: str(oid)}
        allow_population_by_field_name = True

    @root_validator(pre=True)
    def ensure_id(cls, values):
        _id = values.get("_id", None)
        if _id and not values.get("id"):
            values["id"] = str(_id)
        return values


class WebContentResponse(BaseResponse):
    data: list[WebContentResponseData]


WebContentCreatedResponse = BaseResponse[WebContentResponseData]


class WebContentRequest(BaseModel):
    url: str


class WebContentQA(BaseModel):
    answer: str
    documents: list[str]


class WebContentQAResponse(BaseResponse):
    data: WebContentQA
