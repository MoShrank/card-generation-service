from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from adapters.database_models.Content import (
    AnnotationModel,
    ContentSourceType,
    ProcessingStatus,
)


class CreateContentRequest(BaseModel):
    source: str = Field(...)


class UpdateContentData(BaseModel):
    read_status: bool


class ContentData(BaseModel):
    id: str
    source_type: ContentSourceType
    processing_status: ProcessingStatus
    created_at: datetime

    title: Optional[str] = None
    summary: Optional[str] = None

    view_text: Optional[str] = None

    storage_ref: Optional[str] = None
    source: Optional[str] = None

    annotations: list[AnnotationModel] = []
    image: Optional[str] = None

    read_status: bool = False


class UpdateAnnotationsRequest(BaseModel):
    annotations: list[AnnotationModel]
