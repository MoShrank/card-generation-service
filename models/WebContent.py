from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel
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
    summarise: bool
    summary: Optional[str]
    thumbnail: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class WebContentResponseData(BaseModel):
    id: PyObjectID = Field(alias="_id")
    name: str
    url: str
    summary: Optional[str]
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = False
        fields = {"id": "_id"}


class WebContentResponse(BaseResponse):
    data: list[WebContentResponseData]


# WebContentResponse = BaseResponse[list[WebContentResponseData]]

WebContentCreatedResponse = BaseResponse[WebContentResponseData]


class WebContentRequest(BaseModel):
    name: str
    url: str
    summarise: bool


class WebContentQA(BaseModel):
    answer: str
    documents: list[str]


class WebContentQAResponse(BaseResponse):
    data: WebContentQA
