from typing import Any, Literal, Optional

from adapters.database_models.BaseMongoModel import BaseMongoModel

ProcessingStatus = Literal["processing", "processed", "failed"]
ContentSourceType = Literal["pdf", "url", "doi"]


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

    annotations: list[Any] = []
