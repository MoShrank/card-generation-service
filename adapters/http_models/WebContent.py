from typing import Optional

from pydantic import BaseModel, Field

from adapters.http_models.HttpModels import BaseResponse


class WebContentResponseData(BaseModel):
    id: str = Field(alias="_id")
    name: str
    url: str
    summary: Optional[str]
    created_at: str


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
