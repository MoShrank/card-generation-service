from datetime import datetime
from typing import Optional

from typing_extensions import Literal

from adapters.database_models.BaseMongoModel import BaseMongoModel

ProcessingStatus = Literal["processing", "processed", "failed"]


class PDFModel(BaseMongoModel):
    user_id: str
    title: Optional[str]
    storage_ref: Optional[str]
    extracted_markdown: Optional[str]
    summary: Optional[str]
    processing_status: ProcessingStatus
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
