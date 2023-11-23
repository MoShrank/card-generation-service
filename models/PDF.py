from datetime import datetime
from typing import Literal, Optional

from bson import ObjectId
from pydantic import BaseModel
from pydantic.fields import Field

from models.HttpModels import BaseResponse

from .PyObjectID import PyObjectID

ProcessingStatus = Literal["processing", "processed", "failed"]


class PDFModel(BaseModel):
    id: PyObjectID = Field(default_factory=PyObjectID, alias="_id")
    user_id: str
    title: Optional[str]
    extracted_markdown: Optional[str]
    pdf: bytes
    summary: Optional[str]
    processing_status: ProcessingStatus
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class PDFPostResData(BaseModel):
    id: PyObjectID = Field(alias="_id")
    status: ProcessingStatus

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = False
        fields = {"id": "_id"}


PDFPostRes = BaseResponse[PDFPostResData]


class PDFResData(BaseModel):
    id: PyObjectID = Field(alias="_id")
    extracted_markdown: Optional[str]
    # pdf: Optional[bytes]
    processing_status: ProcessingStatus

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = False
        fields = {"id": "_id"}


class PDFResponse(BaseResponse):
    data: list[PDFResData]


class PDFSearchResponseData(BaseModel):
    answer: str
    start_idx: int
    end_idx: int


class PDFSearchResponse(BaseResponse):
    data: list[PDFSearchResponseData]
