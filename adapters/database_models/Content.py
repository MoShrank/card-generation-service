from typing import Literal, Optional

from pydantic import BaseModel

from adapters.database_models.BaseMongoModel import BaseMongoModel

ProcessingStatus = Literal["processing", "processed", "failed"]
ContentSourceType = Literal["pdf", "url", "doi"]


class AnnotationModel(BaseModel):
    start_path: str
    start_offset: int
    end_path: str
    end_offset: int
    color: str
    comment: Optional[str]
    text: str


class ContentModel(BaseMongoModel):
    user_id: str

    title: Optional[str] = None
    summary: Optional[str] = None
    processing_status: ProcessingStatus = "processing"
    source_type: ContentSourceType

    raw_text: Optional[str] = None
    view_text: Optional[str] = None

    storage_ref: Optional[str] = None
    source: Optional[str] = None

    annotations: list[AnnotationModel] = []
    image: Optional[str] = None

    read_status: bool = False
