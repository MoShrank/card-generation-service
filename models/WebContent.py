from pydantic import BaseModel
from pydantic.fields import Field
from PyObjectID import PyObjectID
from datetime import datetime
from typing import Optional
from models.HttpModels import BaseResponse
from typing import List


class WebContent(BaseModel):
    id: PyObjectID = Field(default_factory=PyObjectID, alias="_id")
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


class WebContentResponse(BaseResponse):
    class Data(BaseModel):
        url: str
        summary: bool

    data: List[Data]


class WebContentRequest(BaseModel):
    url: str
    summarise: bool
