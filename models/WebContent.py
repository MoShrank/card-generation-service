from datetime import datetime
from typing import List, Optional

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


class WebContentData(BaseModel):
    name: str
    url: str
    summary: Optional[str]
    created_at: datetime


class WebContentResponse(BaseResponse):

    data: List[WebContentData]


class WebContentCreatedResponse(BaseResponse):
    data: WebContentData


class WebContentRequest(BaseModel):
    name: str
    url: str
    summarise: bool
