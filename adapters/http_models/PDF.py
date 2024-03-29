from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from adapters.database_models.PDF import ProcessingStatus
from adapters.http_models.HttpModels import BaseResponse


class PDFPostResData(BaseModel):
    id: str
    processing_status: ProcessingStatus


PDFPostRes = BaseResponse[PDFPostResData]


class PDFResData(BaseModel):
    id: str
    extracted_markdown: Optional[str]
    processing_status: ProcessingStatus
    created_at: datetime


class PDFResponse(BaseResponse):
    data: list[PDFResData]


class PDFSearchResponseData(BaseModel):
    answer: str
    start_idx: int
    end_idx: int


class PDFSearchResponse(BaseResponse):
    data: list[PDFSearchResponseData]
